// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

/**
 * @title CHAT - Cultural Heritage Asset Tokens
 * @dev ERC1155-based NFT contract for preserving African cultural heritage
 * @author HISA People Chain
 */
contract CHAT is ERC1155, AccessControl, ReentrancyGuard, Pausable {
    using Counters for Counters.Counter;
    
    // Role definitions
    bytes32 public constant ELDER_ROLE = keccak256("ELDER_ROLE");
    bytes32 public constant CURATOR_ROLE = keccak256("CURATOR_ROLE");
    bytes32 public constant VALIDATOR_ROLE = keccak256("VALIDATOR_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    
    // Token counter
    Counters.Counter private _tokenIdCounter;
    
    // CHAT utility token
    IERC20 public chatToken;
    
    // Cultural asset structure
    struct CulturalAsset {
        string name;
        string description;
        string ipfsHash;
        string category; // "oral_tradition", "artifact", "ritual", "art", etc.
        address creator;
        uint256 createdAt;
        uint256 royaltyPercentage; // Basis points (100 = 1%)
        bool isVerified;
        bool isRestricted; // Age/community restricted content
        uint256 conservationFund; // Amount allocated to conservation
        string[] tags;
        mapping(address => bool) accessPermissions;
    }
    
    // Staking structure
    struct StakeInfo {
        uint256 amount;
        uint256 startTime;
        uint256 lockPeriod; // 30, 90, or 365 days
        uint256 lastClaimTime;
        bool isActive;
    }
    
    // Governance proposal structure
    struct Proposal {
        uint256 id;
        string title;
        string description;
        address proposer;
        uint256 startTime;
        uint256 endTime;
        uint256 forVotes;
        uint256 againstVotes;
        bool executed;
        mapping(address => bool) hasVoted;
        mapping(address => bool) voteChoice; // true = for, false = against
    }
    
    // Mappings
    mapping(uint256 => CulturalAsset) public culturalAssets;
    mapping(address => StakeInfo) public stakes;
    mapping(address => bool) public soulboundNFTHolders; // Verified elders/historians
    mapping(uint256 => Proposal) public proposals;
    mapping(address => uint256) public contributorRewards;
    mapping(string => bytes32) public accessControlMerkleRoots;
    
    // State variables
    uint256 public totalStaked;
    uint256 public conservationFundTotal;
    uint256 public proposalCount;
    uint256 public constant ROYALTY_DENOMINATOR = 10000; // For basis points
    uint256 public constant MIN_STAKE_AMOUNT = 1000 * 10**18; // 1000 CHAT tokens
    
    // APY rates for different lock periods (basis points)
    uint256 public constant APY_30_DAYS = 500; // 5%
    uint256 public constant APY_90_DAYS = 1000; // 10%
    uint256 public constant APY_365_DAYS = 1500; // 15%
    
    // Events
    event CulturalAssetCreated(uint256 indexed tokenId, address indexed creator, string name, string category);
    event AssetVerified(uint256 indexed tokenId, address indexed verifier);
    event StakeDeposited(address indexed staker, uint256 amount, uint256 lockPeriod);
    event StakeWithdrawn(address indexed staker, uint256 amount, uint256 rewards);
    event RewardsDistributed(address indexed recipient, uint256 amount);
    event ProposalCreated(uint256 indexed proposalId, address indexed proposer, string title);
    event VoteCast(uint256 indexed proposalId, address indexed voter, bool support, uint256 weight);
    event ConservationFundUpdated(uint256 indexed tokenId, uint256 amount);
    event AccessGranted(uint256 indexed tokenId, address indexed user);
    event SoulboundNFTIssued(address indexed recipient);
    
    constructor(
        string memory uri,
        address _chatToken
    ) ERC1155(uri) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);
        chatToken = IERC20(_chatToken);
    }
    
    /**
     * @dev Create a new cultural heritage asset
     */
    function createCulturalAsset(
        string memory name,
        string memory description,
        string memory ipfsHash,
        string memory category,
        uint256 royaltyPercentage,
        bool isRestricted,
        string[] memory tags,
        uint256 supply
    ) external returns (uint256) {
        require(bytes(name).length > 0, "Name cannot be empty");
        require(bytes(ipfsHash).length > 0, "IPFS hash required");
        require(royaltyPercentage <= 1000, "Royalty too high"); // Max 10%
        
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        
        CulturalAsset storage asset = culturalAssets[tokenId];
        asset.name = name;
        asset.description = description;
        asset.ipfsHash = ipfsHash;
        asset.category = category;
        asset.creator = msg.sender;
        asset.createdAt = block.timestamp;
        asset.royaltyPercentage = royaltyPercentage;
        asset.isRestricted = isRestricted;
        asset.tags = tags;
        
        _mint(msg.sender, tokenId, supply, "");
        
        emit CulturalAssetCreated(tokenId, msg.sender, name, category);
        return tokenId;
    }
    
    /**
     * @dev Verify a cultural asset (only elders/curators)
     */
    function verifyAsset(uint256 tokenId) external onlyRole(ELDER_ROLE) {
        require(exists(tokenId), "Token does not exist");
        culturalAssets[tokenId].isVerified = true;
        emit AssetVerified(tokenId, msg.sender);
    }
    
    /**
     * @dev Stake CHAT tokens
     */
    function stakeCHAT(uint256 amount, uint256 lockPeriod) external nonReentrant {
        require(amount >= MIN_STAKE_AMOUNT, "Minimum stake not met");
        require(
            lockPeriod == 30 days || lockPeriod == 90 days || lockPeriod == 365 days,
            "Invalid lock period"
        );
        require(!stakes[msg.sender].isActive, "Already staking");
        
        require(chatToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        
        stakes[msg.sender] = StakeInfo({
            amount: amount,
            startTime: block.timestamp,
            lockPeriod: lockPeriod,
            lastClaimTime: block.timestamp,
            isActive: true
        });
        
        totalStaked += amount;
        emit StakeDeposited(msg.sender, amount, lockPeriod);
    }
    
    /**
     * @dev Withdraw staked tokens and claim rewards
     */
    function withdrawStake() external nonReentrant {
        StakeInfo storage stake = stakes[msg.sender];
        require(stake.isActive, "No active stake");
        require(block.timestamp >= stake.startTime + stake.lockPeriod, "Lock period not over");
        
        uint256 rewards = calculateRewards(msg.sender);
        uint256 totalAmount = stake.amount + rewards;
        
        stake.isActive = false;
        totalStaked -= stake.amount;
        
        require(chatToken.transfer(msg.sender, totalAmount), "Transfer failed");
        
        emit StakeWithdrawn(msg.sender, stake.amount, rewards);
    }
    
    /**
     * @dev Calculate staking rewards
     */
    function calculateRewards(address staker) public view returns (uint256) {
        StakeInfo storage stake = stakes[staker];
        if (!stake.isActive) return 0;
        
        uint256 timeStaked = block.timestamp - stake.lastClaimTime;
        uint256 apyRate;
        
        if (stake.lockPeriod == 30 days) {
            apyRate = APY_30_DAYS;
        } else if (stake.lockPeriod == 90 days) {
            apyRate = APY_90_DAYS;
        } else {
            apyRate = APY_365_DAYS;
        }
        
        return (stake.amount * apyRate * timeStaked) / (ROYALTY_DENOMINATOR * 365 days);
    }
    
    /**
     * @dev Grant access to restricted content using Merkle proof
     */
    function grantAccess(
        uint256 tokenId,
        bytes32[] calldata merkleProof,
        string memory accessType
    ) external {
        require(exists(tokenId), "Token does not exist");
        require(culturalAssets[tokenId].isRestricted, "Asset not restricted");
        
        bytes32 leaf = keccak256(abi.encodePacked(msg.sender, tokenId));
        bytes32 merkleRoot = accessControlMerkleRoots[accessType];
        
        require(MerkleProof.verify(merkleProof, merkleRoot, leaf), "Invalid proof");
        
        culturalAssets[tokenId].accessPermissions[msg.sender] = true;
        emit AccessGranted(tokenId, msg.sender);
    }
    
    /**
     * @dev Issue Soulbound NFT to verified elders/historians
     */
    function issueSoulboundNFT(address recipient) external onlyRole(ELDER_ROLE) {
        require(!soulboundNFTHolders[recipient], "Already has SBT");
        soulboundNFTHolders[recipient] = true;
        _grantRole(ELDER_ROLE, recipient);
        emit SoulboundNFTIssued(recipient);
    }
    
    /**
     * @dev Create governance proposal
     */
    function createProposal(
        string memory title,
        string memory description,
        uint256 votingPeriod
    ) external returns (uint256) {
        require(soulboundNFTHolders[msg.sender] || hasRole(ELDER_ROLE, msg.sender), "Not authorized");
        
        uint256 proposalId = proposalCount++;
        Proposal storage proposal = proposals[proposalId];
        
        proposal.id = proposalId;
        proposal.title = title;
        proposal.description = description;
        proposal.proposer = msg.sender;
        proposal.startTime = block.timestamp;
        proposal.endTime = block.timestamp + votingPeriod;
        
        emit ProposalCreated(proposalId, msg.sender, title);
        return proposalId;
    }
    
    /**
     * @dev Vote on governance proposal
     */
    function vote(uint256 proposalId, bool support) external {
        Proposal storage proposal = proposals[proposalId];
        require(block.timestamp >= proposal.startTime && block.timestamp <= proposal.endTime, "Voting not active");
        require(!proposal.hasVoted[msg.sender], "Already voted");
        
        uint256 votingPower = getVotingPower(msg.sender);
        require(votingPower > 0, "No voting power");
        
        proposal.hasVoted[msg.sender] = true;
        proposal.voteChoice[msg.sender] = support;
        
        if (support) {
            proposal.forVotes += votingPower;
        } else {
            proposal.againstVotes += votingPower;
        }
        
        emit VoteCast(proposalId, msg.sender, support, votingPower);
    }
    
    /**
     * @dev Calculate voting power based on stake and SBT status
     */
    function getVotingPower(address voter) public view returns (uint256) {
        uint256 power = 0;
        
        // Staked tokens provide voting power
        if (stakes[voter].isActive) {
            power += stakes[voter].amount / 1e18; // 1 CHAT = 1 vote
        }
        
        // SBT holders get bonus voting power
        if (soulboundNFTHolders[voter]) {
            power += 1000; // Bonus votes for verified elders
        }
        
        return power;
    }
    
    /**
     * @dev Distribute rewards to contributors
     */
    function distributeRewards(address recipient, uint256 amount) external onlyRole(CURATOR_ROLE) {
        require(chatToken.transfer(recipient, amount), "Transfer failed");
        contributorRewards[recipient] += amount;
        emit RewardsDistributed(recipient, amount);
    }
    
    /**
     * @dev Add to conservation fund
     */
    function addToConservationFund(uint256 tokenId, uint256 amount) external {
        require(exists(tokenId), "Token does not exist");
        require(chatToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        
        culturalAssets[tokenId].conservationFund += amount;
        conservationFundTotal += amount;
        
        emit ConservationFundUpdated(tokenId, amount);
    }
    
    /**
     * @dev Set access control Merkle root
     */
    function setAccessControlMerkleRoot(string memory accessType, bytes32 merkleRoot) external onlyRole(ELDER_ROLE) {
        accessControlMerkleRoots[accessType] = merkleRoot;
    }
    
    /**
     * @dev Check if token exists
     */
    function exists(uint256 tokenId) public view returns (bool) {
        return culturalAssets[tokenId].creator != address(0);
    }
    
    /**
     * @dev Get cultural asset details
     */
    function getCulturalAsset(uint256 tokenId) external view returns (
        string memory name,
        string memory description,
        string memory ipfsHash,
        string memory category,
        address creator,
        uint256 createdAt,
        uint256 royaltyPercentage,
        bool isVerified,
        bool isRestricted,
        uint256 conservationFund
    ) {
        CulturalAsset storage asset = culturalAssets[tokenId];
        return (
            asset.name,
            asset.description,
            asset.ipfsHash,
            asset.category,
            asset.creator,
            asset.createdAt,
            asset.royaltyPercentage,
            asset.isVerified,
            asset.isRestricted,
            asset.conservationFund
        );
    }
    
    /**
     * @dev Emergency functions
     */
    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }
    
    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Override required by Solidity
     */
    function supportsInterface(bytes4 interfaceId) public view virtual override(ERC1155, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}