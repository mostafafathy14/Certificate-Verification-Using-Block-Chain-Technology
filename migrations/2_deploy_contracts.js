const CertificateRegistry = artifacts.require("CertificateRegistry");

module.exports = async function (deployer, network, accounts) {
    await deployer.deploy(CertificateRegistry, accounts[0]); // Pass the first Ganache account as initialOwner
};