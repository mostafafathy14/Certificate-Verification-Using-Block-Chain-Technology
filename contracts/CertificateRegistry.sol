// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";

contract CertificateRegistry is Ownable {
    struct Certificate {
        string cid;
        address issuer;
        bool revoked;
        uint256 issuedAt;
        string uid;
        string candidateName;
        string courseName;
        string organization;
    }

    mapping(string => Certificate) public certificates;
    mapping(address => bool) public isIssuer;

    event CertificateIssued(string certificateId, string cid, address issuer);
    event CertificateRevoked(string certificateId);

    // Constructor to initialize owner and add initial issuer
    constructor(address initialOwner) Ownable(initialOwner) {
        isIssuer[initialOwner] = true;
    }

    // Issue a new certificate
    function issueCertificate(
        string memory certificateId,
        string memory cid,
        string memory uid,
        string memory candidateName,
        string memory courseName,
        string memory organization
    ) public {
        require(bytes(certificates[certificateId].cid).length == 0, "Certificate already exists");

        certificates[certificateId] = Certificate({
            cid: cid,
            issuer: msg.sender,
            revoked: false,
            issuedAt: block.timestamp,
            uid: uid,
            candidateName: candidateName,
            courseName: courseName,
            organization: organization
        });

        emit CertificateIssued(certificateId, cid, msg.sender);
    }

    // Revoke an existing certificate
    function revokeCertificate(string memory certificateId) public {
        require(certificates[certificateId].issuer == msg.sender, "Only issuer can revoke");
        certificates[certificateId].revoked = true;
        emit CertificateRevoked(certificateId);
    }

    // Verify a certificate
    function verifyCertificate(string memory certificateId) public view returns (
        bool exists,
        string memory uid,
        string memory candidateName,
        string memory courseName,
        string memory organization,
        string memory cid,
        address issuer,
        bool revoked,
        uint256 issuedAt
    ) {
        Certificate memory cert = certificates[certificateId];
        exists = bytes(cert.cid).length > 0;

        return (
            exists,
            cert.uid,
            cert.candidateName,
            cert.courseName,
            cert.organization,
            cert.cid,
            cert.issuer,
            cert.revoked,
            cert.issuedAt
        );
    }
}
