// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title VeriChain — Blockchain Identity & Digital Asset Platform
/// @notice Manages decentralized identities, NFT-based assets, guardian recovery, and audit logging
contract VeriChain {

    // ══════════════════════════════════════════════════════
    //  STATE
    // ══════════════════════════════════════════════════════

    address public superAdmin;

    // Admins mapping
    mapping(address => bool) public admins;

    // ── IDENTITY ──
    struct UserProfile {
        address wallet;
        string  profileUri;   // IPFS URI
        bool    isRegistered;
    }
    mapping(address => UserProfile) private profiles;

    // ── ASSETS ──
    struct Asset {
        uint256 id;
        string  assetType;    // gold, certificate, stock, crypto, nft, document
        string  assetName;
        uint256 quantity;
        string  metadataUri;  // IPFS URI
        address owner;
        bool    isValid;
    }
    uint256 public assetCounter;
    mapping(uint256 => Asset) public assets;
    mapping(address => uint256[]) private ownerAssets;

    // ── GUARDIANS ──
    // identity => guardian list (we use the wallet itself as identity)
    mapping(address => address[]) private guardians;
    mapping(address => uint256) private recoveryThreshold;

    // ── RECOVERY ──
    enum RecoveryStatus { None, Pending, Executed, Cancelled }
    struct RecoveryRequest {
        uint256        id;
        address        identity;
        address        proposedNewOwner;
        uint256        approvalCount;
        RecoveryStatus status;
    }
    uint256 public recoveryCounter;
    mapping(uint256 => RecoveryRequest) public recoveryRequests;
    mapping(address => uint256)          public activeRecoveryId;
    mapping(uint256 => mapping(address => bool)) private hasApproved;

    // ══════════════════════════════════════════════════════
    //  EVENTS
    // ══════════════════════════════════════════════════════

    event UserRegistered(address indexed wallet, string profileUri);
    event AssetMinted(uint256 indexed id, address indexed owner, string assetType);
    event AssetRevoked(uint256 indexed id);
    event AdminAdded(address indexed admin);
    event GuardianAdded(address indexed identity, address guardian);
    event GuardianRemoved(address indexed identity, address guardian);
    event RecoveryRequested(uint256 indexed recoveryId, address indexed identity, address proposedNewOwner);
    event RecoveryApproved(uint256 indexed recoveryId, address guardian);
    event RecoveryExecuted(uint256 indexed recoveryId, address indexed identity, address newOwner);
    event RecoveryCancelled(uint256 indexed recoveryId);
    event AuditLog(string action, string details, address indexed actor, uint256 timestamp);

    // ══════════════════════════════════════════════════════
    //  MODIFIERS
    // ══════════════════════════════════════════════════════

    modifier onlySuperAdmin() {
        require(msg.sender == superAdmin, "Not super admin");
        _;
    }

    modifier onlyAdmin() {
        require(admins[msg.sender] || msg.sender == superAdmin, "Not an admin");
        _;
    }

    // ══════════════════════════════════════════════════════
    //  CONSTRUCTOR
    // ══════════════════════════════════════════════════════

    constructor() {
        superAdmin = msg.sender;
        admins[msg.sender] = true;
    }

    // ══════════════════════════════════════════════════════
    //  ROLE MANAGEMENT
    // ══════════════════════════════════════════════════════

    function addAdmin(address _admin) external onlySuperAdmin {
        require(_admin != address(0), "Zero address");
        admins[_admin] = true;
        emit AdminAdded(_admin);
    }

    function revokeAdmin(address _admin) external onlySuperAdmin {
        require(_admin != superAdmin, "Cannot revoke super admin");
        admins[_admin] = false;
    }

    // ══════════════════════════════════════════════════════
    //  IDENTITY
    // ══════════════════════════════════════════════════════

    function registerUser(address _wallet, string calldata _profileUri) external onlyAdmin {
        require(_wallet != address(0), "Zero address");
        require(!profiles[_wallet].isRegistered, "Already registered");
        profiles[_wallet] = UserProfile({
            wallet:       _wallet,
            profileUri:   _profileUri,
            isRegistered: true
        });
        recoveryThreshold[_wallet] = 1; // default threshold
        emit UserRegistered(_wallet, _profileUri);
    }

    function getUserProfile(address _wallet) external view returns (address, string memory, bool) {
        UserProfile memory p = profiles[_wallet];
        return (p.wallet, p.profileUri, p.isRegistered);
    }

    // Allow re-registration to update URI (admin only)
    function updateProfileUri(address _wallet, string calldata _profileUri) external onlyAdmin {
        require(profiles[_wallet].isRegistered, "Not registered");
        profiles[_wallet].profileUri = _profileUri;
    }

    // ══════════════════════════════════════════════════════
    //  ASSETS
    // ══════════════════════════════════════════════════════

    function mintAsset(
        address _owner,
        string calldata _assetType,
        string calldata _assetName,
        uint256 _quantity,
        string calldata _metadataUri
    ) external onlyAdmin {
        require(_owner != address(0), "Zero address");
        require(_quantity > 0, "Quantity must be > 0");

        assetCounter++;
        assets[assetCounter] = Asset({
            id:          assetCounter,
            assetType:   _assetType,
            assetName:   _assetName,
            quantity:    _quantity,
            metadataUri: _metadataUri,
            owner:       _owner,
            isValid:     true
        });
        ownerAssets[_owner].push(assetCounter);

        emit AssetMinted(assetCounter, _owner, _assetType);
    }

    function revokeAsset(uint256 _assetId) external onlyAdmin {
        require(assets[_assetId].id != 0, "Asset not found");
        require(assets[_assetId].isValid, "Already revoked");
        assets[_assetId].isValid = false;
        emit AssetRevoked(_assetId);
    }

    function getOwnerAssets(address _owner) external view returns (uint256[] memory) {
        return ownerAssets[_owner];
    }

    // ══════════════════════════════════════════════════════
    //  GUARDIANS
    // ══════════════════════════════════════════════════════

    function addGuardian(address _guardian) external {
        require(_guardian != address(0), "Zero address");
        require(_guardian != msg.sender, "Cannot be own guardian");

        address[] storage g = guardians[msg.sender];
        for (uint i = 0; i < g.length; i++) {
            require(g[i] != _guardian, "Already a guardian");
        }
        g.push(_guardian);
        emit GuardianAdded(msg.sender, _guardian);
    }

    function removeGuardian(address _guardian) external {
        address[] storage g = guardians[msg.sender];
        for (uint i = 0; i < g.length; i++) {
            if (g[i] == _guardian) {
                g[i] = g[g.length - 1];
                g.pop();
                emit GuardianRemoved(msg.sender, _guardian);
                return;
            }
        }
        revert("Guardian not found");
    }

    function setRecoveryThreshold(uint256 _threshold) external {
        require(_threshold >= 1, "Threshold must be >= 1");
        require(_threshold <= guardians[msg.sender].length, "Threshold exceeds guardian count");
        recoveryThreshold[msg.sender] = _threshold;
    }

    // Admin can also add guardians for a user (e.g. onboarding)
    function addGuardianFor(address _identity, address _guardian) external onlyAdmin {
        require(_guardian != address(0), "Zero address");
        guardians[_identity].push(_guardian);
        emit GuardianAdded(_identity, _guardian);
    }

    function getIdentity(address _wallet) external view returns (address) {
        return _wallet; // In this design, identity = wallet address
    }

    function getGuardians(address _identity) external view returns (address[] memory) {
        return guardians[_identity];
    }

    function getRecoveryThreshold(address _identity) external view returns (uint256) {
        return recoveryThreshold[_identity];
    }

    // ══════════════════════════════════════════════════════
    //  RECOVERY
    // ══════════════════════════════════════════════════════

    function requestRecovery(address _identityAddress, address _newOwner) external {
        require(_identityAddress != address(0), "Zero address");
        require(_newOwner != address(0), "Zero address");
        require(activeRecoveryId[_identityAddress] == 0, "Recovery already active");

        recoveryCounter++;
        recoveryRequests[recoveryCounter] = RecoveryRequest({
            id:               recoveryCounter,
            identity:         _identityAddress,
            proposedNewOwner: _newOwner,
            approvalCount:    0,
            status:           RecoveryStatus.Pending
        });
        activeRecoveryId[_identityAddress] = recoveryCounter;

        emit RecoveryRequested(recoveryCounter, _identityAddress, _newOwner);
    }

    function approveRecovery(uint256 _recoveryId) external {
        RecoveryRequest storage req = recoveryRequests[_recoveryId];
        require(req.status == RecoveryStatus.Pending, "Not pending");
        require(!hasApproved[_recoveryId][msg.sender], "Already approved");

        // Check caller is a guardian
        address[] memory g = guardians[req.identity];
        bool isGuardian = false;
        for (uint i = 0; i < g.length; i++) {
            if (g[i] == msg.sender) { isGuardian = true; break; }
        }
        require(isGuardian || msg.sender == superAdmin, "Not a guardian");

        hasApproved[_recoveryId][msg.sender] = true;
        req.approvalCount++;

        emit RecoveryApproved(_recoveryId, msg.sender);

        // Auto-execute if threshold met
        uint256 threshold = recoveryThreshold[req.identity];
        if (threshold == 0) threshold = 1;
        if (req.approvalCount >= threshold) {
            _executeRecovery(_recoveryId);
        }
    }

    function executeRecovery(uint256 _recoveryId) external {
        RecoveryRequest storage req = recoveryRequests[_recoveryId];
        require(req.status == RecoveryStatus.Pending, "Not pending");
        uint256 threshold = recoveryThreshold[req.identity];
        if (threshold == 0) threshold = 1;
        require(req.approvalCount >= threshold, "Insufficient approvals");
        _executeRecovery(_recoveryId);
    }

    function _executeRecovery(uint256 _recoveryId) internal {
        RecoveryRequest storage req = recoveryRequests[_recoveryId];
        req.status = RecoveryStatus.Executed;

        // Transfer all assets to new owner
        uint256[] memory assetIds = ownerAssets[req.identity];
        for (uint i = 0; i < assetIds.length; i++) {
            if (assets[assetIds[i]].isValid) {
                assets[assetIds[i]].owner = req.proposedNewOwner;
                ownerAssets[req.proposedNewOwner].push(assetIds[i]);
            }
        }
        // Transfer profile
        profiles[req.proposedNewOwner] = profiles[req.identity];
        profiles[req.proposedNewOwner].wallet = req.proposedNewOwner;

        activeRecoveryId[req.identity] = 0;
        emit RecoveryExecuted(_recoveryId, req.identity, req.proposedNewOwner);
    }

    function cancelRecovery(uint256 _recoveryId) external {
        RecoveryRequest storage req = recoveryRequests[_recoveryId];
        require(req.status == RecoveryStatus.Pending, "Not pending");
        require(
            msg.sender == req.identity || admins[msg.sender] || msg.sender == superAdmin,
            "Not authorized"
        );
        req.status = RecoveryStatus.Cancelled;
        activeRecoveryId[req.identity] = 0;
        emit RecoveryCancelled(_recoveryId);
    }

    // ══════════════════════════════════════════════════════
    //  AUDIT
    // ══════════════════════════════════════════════════════

    function logAudit(string calldata _action, string calldata _details) external {
        emit AuditLog(_action, _details, msg.sender, block.timestamp);
    }
}
