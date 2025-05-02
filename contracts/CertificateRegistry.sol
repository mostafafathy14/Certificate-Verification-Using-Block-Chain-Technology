// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";

contract CertificateRegistry is Ownable {
    struct Certificate {
        string cid; // IPFS Content Identifier
        address issuer;
        bool revoked;
    }

    mapping(string => Certificate) public certificates;

    event CertificateIssued(string certificateId, string cid, address issuer);
    event CertificateRevoked(string certificateId);

    // Constructor to initialize Ownable with an initial owner
    constructor(address initialOwner) Ownable(initialOwner) {
    }

    // Issue a new certificate
    function issueCertificate(string memory certificateId, string memory cid) public onlyOwner {
        require(bytes(certificates[certificateId].cid).length == 0, "Certificate already exists");
        certificates[certificateId] = Certificate(cid, msg.sender, false);
        emit CertificateIssued(certificateId, cid, msg.sender);
    }

    // Revoke an existing certificate
    function revokeCertificate(string memory certificateId) public onlyOwner {
        require(certificates[certificateId].issuer == msg.sender, "Only issuer can revoke");
        certificates[certificateId].revoked = true;
        emit CertificateRevoked(certificateId);
    }

    // Verify a certificate
    function verifyCertificate(string memory certificateId) public view returns (bool, address, bool) {
        Certificate memory cert = certificates[certificateId];
        return (bytes(cert.cid).length > 0, cert.issuer, cert.revoked);
    }
}