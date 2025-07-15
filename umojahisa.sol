// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * UMOJA Tokenomics Ecosystem - Clean, Gas-Optimized
 */

// ============================================================================
// UMOJA TOKEN (UMOT)
// ============================================================================

contract UmojaToken is ERC20, Ownable, ReentrancyGuard {
    uint256 public constant MAX_SUPPLY = 21_000_000_000 * 10**18;

    uint128 public totalBackingValue;
    uint128 public lastBackingUpdate;

    mapping(address => uint256) public stakingBalance;
    mapping(address => uint32) public stakingTimestamp;

    uint256 public constant GOVERNANCE_THRESHOLD = 1000 * 10**18;

    event TokensStaked(address indexed user, uint256 amount);
    event TokensUnstaked(address indexed user, uint256 amount, uint256 rewards);
    event BackingUpdated(uint128 value);

    constructor(address initialOwner) ERC20("UMOJA Token", "UMOT") Ownable(initialOwner) {
        _mint(initialOwner, MAX_SUPPLY);
    }

    function stake(uint256 _amount) external nonReentrant {
        require(_amount > 0 && balanceOf(msg.sender) >= _amount, "Invalid amount");
        _transfer(msg.sender, address(this), _amount);
        stakingBalance[msg.sender] += _amount;
        stakingTimestamp[msg.sender] = uint32(block.timestamp);
        emit TokensStaked(msg.sender, _amount);
    }

    function unstake(uint256 _amount) external nonReentrant {
        require(stakingBalance[msg.sender] >= _amount, "Insufficient staking balance");

        uint256 timeStaked = block.timestamp - stakingTimestamp[msg.sender];
        uint256 rewards = (stakingBalance[msg.sender] * 800 * timeStaked) / (10000 * 365 days);

        stakingBalance[msg.sender] -= _amount;
        stakingTimestamp[msg.sender] = uint32(block.timestamp);

        _transfer(address(this), msg.sender, _amount);
        if (rewards > 0) _mint(msg.sender, rewards);

        emit TokensUnstaked(msg.sender, _amount, rewards);
    }

    function updateBacking(uint128 _value) external onlyOwner {
        totalBackingValue = _value;
        lastBackingUpdate = uint128(block.timestamp);
        emit BackingUpdated(_value);
    }

    function hasVotingPower(address _user) external view returns (bool) {
        return balanceOf(_user) >= GOVERNANCE_THRESHOLD;
    }
}

// ============================================================================
// UMOJA STABLE (UMOS)
// ============================================================================

contract UmojaStable is ERC20, Ownable {
    uint256 public totalBacking;
    mapping(address => bool) public authorizedMinters;

    uint256 public constant TARGET_PRICE = 1 * 10**18;

    event MinterUpdated(address indexed minter, bool authorized);
    event BackingUpdated(uint256 value);

    constructor(address initialOwner) ERC20("UMOJA Stable", "UMOS") Ownable(initialOwner) {}

    function mint(address _to, uint256 _amount) external {
        require(authorizedMinters[msg.sender], "Unauthorized");
        _mint(_to, _amount);
    }

    function burn(uint256 _amount) external {
        _burn(msg.sender, _amount);
    }

    function setMinter(address _minter, bool _authorized) external onlyOwner {
        authorizedMinters[_minter] = _authorized;
        emit MinterUpdated(_minter, _authorized);
    }

    function updateBacking(uint256 _value) external onlyOwner {
        totalBacking = _value;
        emit BackingUpdated(_value);
    }

    function stabilityAction(bool _mintTokens, uint256 _amount) external onlyOwner {
        if (_mintTokens) {
            _mint(owner(), _amount);
        } else {
            _burn(owner(), _amount);
        }
    }
}

// ============================================================================
// UMOJA OPTIONS (UMOO)
// ============================================================================

contract UmojaOptions is ERC20, Ownable, ReentrancyGuard {
    uint256 public constant MAX_SUPPLY = 210_000_000_000_000 * 10**18;
    uint256 public constant ANNUAL_EMISSION = 210_000_000_000 * 10**18;

    struct Option {
        address holder;
        uint256 strikePrice;
        uint256 premium;
        uint32 expiry;
        bool isCall;
        bool isActive;
    }

    mapping(uint256 => Option) public options;
    uint256 public nextOptionId = 1;

    uint256 public lastEmissionTime;
    uint256 public totalEmitted;

    uint256 public gasTokenRate = 1000;

    event OptionCreated(uint256 indexed id, address indexed holder, bool isCall);
    event OptionExercised(uint256 indexed id, uint256 payout);
    event TokensBurned(uint256 amount);

    constructor(address initialOwner) ERC20("UMOJA Options", "UMOO") Ownable(initialOwner) {
        lastEmissionTime = block.timestamp;
    }

    function annualEmission() external onlyOwner {
        require(block.timestamp >= lastEmissionTime + 365 days, "Too early");
        require(totalEmitted < MAX_SUPPLY, "Max supply reached");

        uint256 amount = ANNUAL_EMISSION;
        if (totalEmitted + amount > MAX_SUPPLY) {
            amount = MAX_SUPPLY - totalEmitted;
        }

        _mint(owner(), amount);
        totalEmitted += amount;
        lastEmissionTime = block.timestamp;
    }

    function createOption(
        bool _isCall,
        uint256 _strikePrice,
        uint32 _expiry,
        uint256 _premium
    ) external nonReentrant {
        require(_expiry > block.timestamp, "Invalid expiry");
        require(balanceOf(msg.sender) >= _premium, "Insufficient balance");

        _transfer(msg.sender, address(this), _premium);

        options[nextOptionId] = Option({
            holder: msg.sender,
            strikePrice: _strikePrice,
            premium: _premium,
            expiry: _expiry,
            isCall: _isCall,
            isActive: true
        });

        emit OptionCreated(nextOptionId, msg.sender, _isCall);
        nextOptionId++;
    }

    function exerciseOption(uint256 _optionId) external nonReentrant {
        Option storage option = options[_optionId];
        require(option.holder == msg.sender, "Not holder");
        require(option.isActive, "Not active");
        require(block.timestamp <= option.expiry, "Expired");

        uint256 payout = option.premium / 2;

        _mint(msg.sender, payout);
        _burn(address(this), option.premium);

        option.isActive = false;
        emit OptionExercised(_optionId, payout);
        emit TokensBurned(option.premium);
    }

    function payGas(uint256 _gasUsed) external {
        uint256 tokensRequired = _gasUsed / gasTokenRate;
        require(balanceOf(msg.sender) >= tokensRequired, "Insufficient tokens");

        _burn(msg.sender, tokensRequired);
        emit TokensBurned(tokensRequired);
    }

    function expireOption(uint256 _optionId) external {
        Option storage option = options[_optionId];
        require(block.timestamp > option.expiry, "Not expired");
        require(option.isActive, "Already inactive");

        _burn(address(this), option.premium);
        option.isActive = false;
        emit TokensBurned(option.premium);
    }
}
