// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title HISA Token Contract
 * @dev Simple ERC20 token for the HISA People Chain ecosystem
 * @notice This token represents ownership in Africa's digital economy
 */
contract HISAToken {
    
    // ============ TOKEN INFORMATION ============
    
    string public name = "HISA Token";           // Full name of the token
    string public symbol = "HISA";               // Short symbol (ticker)
    uint8 public decimals = 18;                 // Number of decimal places (like ETH)
    uint256 public totalSupply = 3000000000 * 10**18; // 3 billion tokens total
    
    // ============ STORAGE MAPPINGS ============
    
    // Track how many tokens each address owns
    mapping(address => uint256) public balanceOf;
    
    // Track spending permissions: owner => spender => amount
    // This allows others to spend tokens on your behalf
    mapping(address => mapping(address => uint256)) public allowance;
    
    // ============ EVENTS ============
    
    // Emitted when tokens are transferred between addresses
    event Transfer(address indexed from, address indexed to, uint256 value);
    
    // Emitted when someone approves another address to spend their tokens
    event Approval(address indexed owner, address indexed spender, uint256 value);
    
    // ============ CONSTRUCTOR ============
    
    /**
     * @dev Constructor runs once when contract is deployed
     * @notice Gives all 3 billion tokens to the contract deployer
     */
    constructor() {
        balanceOf[msg.sender] = totalSupply;  // Give all tokens to deployer
    }
    
    // ============ CORE FUNCTIONS ============
    
    /**
     * @dev Transfer tokens from your account to another address
     * @param to The address to send tokens to
     * @param amount How many tokens to send (in wei, so 1 token = 10^18)
     * @return bool Returns true if transfer was successful
     */
    function transfer(address to, uint256 amount) external returns (bool) {
        // Check: Make sure sender has enough tokens
        require(balanceOf[msg.sender] >= amount, "Not enough balance");
        
        // Effects: Update balances
        balanceOf[msg.sender] -= amount;  // Subtract from sender
        balanceOf[to] += amount;          // Add to recipient
        
        // Interactions: Emit event for transparency
        emit Transfer(msg.sender, to, amount);
        
        return true;
    }
    
    /**
     * @dev Approve another address to spend your tokens
     * @param spender The address you're giving permission to
     * @param amount How many tokens they can spend
     * @return bool Returns true if approval was successful
     * @notice This is useful for contracts that need to move your tokens
     */
    function approve(address spender, uint256 amount) external returns (bool) {
        // Set the allowance amount
        allowance[msg.sender][spender] = amount;
        
        // Emit approval event
        emit Approval(msg.sender, spender, amount);
        
        return true;
    }
    
    /**
     * @dev Transfer tokens on behalf of another address (if you have permission)
     * @param from The address to take tokens from
     * @param to The address to send tokens to  
     * @param amount How many tokens to transfer
     * @return bool Returns true if transfer was successful
     * @notice The 'from' address must have approved you to spend their tokens
     */
    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        // Check: Make sure the owner has enough tokens
        require(balanceOf[from] >= amount, "Not enough balance");
        
        // Check: Make sure you have permission to spend this amount
        require(allowance[from][msg.sender] >= amount, "Not enough allowance");
        
        // Effects: Update balances
        balanceOf[from] -= amount;           // Subtract from original owner
        balanceOf[to] += amount;             // Add to recipient
        allowance[from][msg.sender] -= amount; // Reduce your spending allowance
        
        // Interactions: Emit transfer event
        emit Transfer(from, to, amount);
        
        return true;
    }
    
    // ============ HELPER FUNCTIONS (Optional) ============
    
    /**
     * @dev Get the token balance of any address
     * @param account The address to check
     * @return uint256 The token balance
     * @notice This is a view function (doesn't cost gas to call)
     */
    function getBalance(address account) external view returns (uint256) {
        return balanceOf[account];
    }
    
    /**
     * @dev Check how many tokens an address is allowed to spend on your behalf
     * @param owner The token owner
     * @param spender The address with spending permission
     * @return uint256 The allowance amount
     */
    function getAllowance(address owner, address spender) external view returns (uint256) {
        return allowance[owner][spender];
    }
}

/*
============ USAGE EXAMPLES ============

1. DEPLOY CONTRACT:
   - Deploy this contract on Remix
   - Deployer gets all 3 billion HISA tokens

2. SEND TOKENS:
   - Call transfer("0x123...", 1000000000000000000) to send 1 HISA token
   - Remember: 1 token = 10^18 wei (because decimals = 18)

3. APPROVE SPENDING:
   - Call approve("0x456...", 5000000000000000000) to let someone spend 5 tokens
   - They can then call transferFrom() to move your tokens

4. CHECK BALANCES:
   - Call balanceOf("0x789...") to see how many tokens an address has
   - Call allowance("0x123...", "0x456...") to see spending permissions

============ SECURITY NOTES ============

- This is a basic ERC20 implementation
- All tokens are created at deployment (no minting)
- No burning mechanism (tokens can't be destroyed)
- No owner controls (fully decentralized)
- Use CEI pattern (Checks-Effects-Interactions) for security

============ HISA ECOSYSTEM CONTEXT ============

This token represents ownership in Africa's digital economy:
- Users earn HISA by verified activities (tree planting, cultural preservation, etc.)
- Used for governance voting in the HISA ecosystem
- Can be traded or used to purchase services
- Represents a stake in the community's success
*/