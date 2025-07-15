// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title JANI HISA - Proof of Growth Smart Contract
/// @notice Rewards verified conservation work with JANI tokens

contract JaniHisa {
    address public admin;
    uint256 public totalNurseries;
    uint256 public totalValidators;
    uint256 public totalMintedTokens;

    struct Nursery {
        address wallet;
        string region;
        uint256 planted;
        bool active;
    }

    struct Validator {
        address wallet;
        bool approved;
        uint256 validations;
    }

    mapping(uint256 => Nursery) public nurseries;
    mapping(address => Validator) public validators;

    event NurseryRegistered(uint256 indexed nurseryId, address indexed wallet, string region);
    event TreePlanted(uint256 indexed nurseryId, uint256 trees);
    event TreeVerified(uint256 indexed nurseryId, address indexed validator);
    event JaniTokenMinted(address indexed beneficiary, uint256 amount);

    modifier onlyAdmin() {
        require(msg.sender == admin, "JANI HISA: Not admin");
        _;
    }

    modifier onlyValidator() {
        require(validators[msg.sender].approved, "JANI HISA: Not a validator");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function registerNursery(address nurseryWallet, string calldata region) external onlyAdmin {
        totalNurseries++;
        nurseries[totalNurseries] = Nursery(nurseryWallet, region, 0, true);
        emit NurseryRegistered(totalNurseries, nurseryWallet, region);
    }

    function approveValidator(address validatorWallet) external onlyAdmin {
        validators[validatorWallet] = Validator(validatorWallet, true, 0);
        totalValidators++;
    }

    function logTreePlanting(uint256 nurseryId, uint256 trees) external {
        Nursery storage nursery = nurseries[nurseryId];
        require(nursery.active, "JANI HISA: Nursery inactive");
        require(msg.sender == nursery.wallet, "JANI HISA: Unauthorized");

        nursery.planted += trees;
        emit TreePlanted(nurseryId, trees);
    }

    function verifyTrees(uint256 nurseryId, uint256 verifiedTrees) external onlyValidator {
        Nursery storage nursery = nurseries[nurseryId];
        require(nursery.planted >= verifiedTrees, "JANI HISA: Over-verification");

        validators[msg.sender].validations++;
        totalMintedTokens += verifiedTrees;

        emit TreeVerified(nurseryId, msg.sender);
        emit JaniTokenMinted(nursery.wallet, verifiedTrees);
    }

    function getNursery(uint256 id) external view returns (Nursery memory) {
        return nurseries[id];
    }

    function getValidator(address addr) external view returns (Validator memory) {
        return validators[addr];
    }
}
