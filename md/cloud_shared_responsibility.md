# Cloud Shared Responsibility: What It Means in Practice

One of the most persistent misconceptions about cloud computing is that moving to the cloud means security becomes the provider's problem. It doesn't. Every major cloud provider publishes a shared responsibility model that delineates exactly what they secure versus what you, the customer, must secure. Understanding that line is not optional. Ignoring it is how organizations end up breached and then confused about why their cloud provider didn't stop it.

## The Core Idea

Cloud security responsibility is divided between the provider and the customer. The provider is responsible for the security of the cloud infrastructure itself. The customer is responsible for security in the cloud: what they put there, how they configure it, and who they allow to access it.

Where exactly the line falls depends on which service model you're using.

## How the Model Varies by Service Type

The three fundamental cloud service models carry different responsibility splits. As you move up the stack from infrastructure to platform to software, the provider takes on more responsibility and you take on less.

### IaaS: Infrastructure as a Service

Examples: AWS EC2, Azure Virtual Machines, Google Compute Engine.

The provider secures the physical hardware, the data center, the hypervisor layer, and the network fabric underlying the virtualization platform. Everything above the hypervisor is yours.

**Provider responsibility**: Physical security, hardware, networking infrastructure, virtualization platform, storage hardware.

**Customer responsibility**: The operating system (patching, hardening), applications running on it, the data stored, network configuration (security groups, NACLs, VPC design), identity and access management, and encryption.

When you spin up an EC2 instance, you're responsible for that instance. If you don't patch the OS, that's on you. If you leave port 22 open to 0.0.0.0/0, that's on you. AWS will not email you to say your instance has an unpatched kernel vulnerability.

### PaaS: Platform as a Service

Examples: AWS RDS, Azure App Service, Google Cloud SQL.

The provider manages the OS, the runtime environment, and in database services, the database engine itself. You don't have to think about patching PostgreSQL on RDS; AWS handles that.

**Provider responsibility**: Infrastructure, OS, runtime, middleware, the platform service itself.

**Customer responsibility**: The data you store, access controls to the service, application-level security, and how you configure the service.

With RDS, the database engine stays patched, but you're still responsible for who has database credentials, whether the database is publicly accessible, whether sensitive data is encrypted, and whether database audit logging is enabled.

### SaaS: Software as a Service

Examples: Microsoft 365, Salesforce, Google Workspace, Slack.

The provider manages essentially everything: infrastructure, OS, application code, availability. You consume the service.

**Provider responsibility**: Almost everything in the stack.

**Customer responsibility**: User access management (who has accounts, what permissions, are accounts disabled when employees leave), data classification and handling policies, configuration of security settings within the application, and compliance with your own regulatory requirements.

A Microsoft 365 breach caused by a compromised admin account with no MFA is not Microsoft's fault. The provider gave you MFA; you chose not to enforce it.

## What the Provider Is Not Responsible For

This is where organizations get into trouble. The shared responsibility model does not cover:

**Customer misconfiguration**: An S3 bucket configured to allow public access, an RDS instance with a public endpoint and a weak password, a Lambda function with overpermissive IAM. These are configuration choices made by the customer, and the provider is not responsible for the consequences.

**Weak IAM policies**: Giving every user AdministratorAccess, storing long-lived access keys in GitHub repositories, not rotating credentials, not enforcing MFA on privileged accounts. The provider gives you the IAM tools; using them correctly is your job.

**Unencrypted data**: AWS S3 supports multiple encryption options. If you store sensitive data without enabling encryption, that's a customer decision.

**Exposed APIs and applications**: The provider secures the network plumbing. If you deploy an application with a SQL injection vulnerability, that vulnerability is yours.

**Access control within applications**: In SaaS environments, if you give a contractor admin access and they misuse it, that's an access management failure on your side.

## Real-World Examples of the Confusion

The Capital One breach in 2019 is the canonical example. An attacker exploited a misconfigured WAF running on an EC2 instance to perform a server-side request forgery attack, then used that SSRF to access the EC2 instance metadata service and retrieve IAM role credentials. Those credentials had overpermissive access to S3 buckets containing customer data.

Was this an AWS breach? No. AWS's infrastructure functioned correctly. The WAF misconfiguration was a Capital One configuration error. The overpermissive IAM role was a Capital One IAM design error. The metadata service credential theft was a well-known attack against IMDSv1 that AWS had already addressed with IMDSv2.

Thousands of organizations have exposed S3 buckets containing backups, PII, internal documents, and plaintext credentials. In almost every case, the exposure resulted from a customer-side configuration choice, not a provider-side vulnerability.

## Core Customer Responsibilities Across All Models

Regardless of whether you're running IaaS, PaaS, or SaaS, certain responsibilities always fall to the customer:

**IAM hygiene**: Least privilege. No standing high-privilege accounts. No overpermissive roles. Regular access reviews. MFA on everything. No sharing credentials. Rotate and revoke long-lived keys.

**Encryption in transit and at rest**: Use HTTPS everywhere. Enable encryption at rest for storage services. The provider gives you the tools; you have to turn them on and configure them correctly.

**Logging and monitoring**: Enable CloudTrail (AWS), Azure Monitor/Diagnostic Logs, or GCP Cloud Audit Logs. Enable access logging on storage services. Set up alerting. If you're not logging, you can't detect incidents and you can't investigate after the fact.

**Patch what you own**: In IaaS environments, OS and application patching is your responsibility. Have a patching process. Know what's running. Act on critical vulnerabilities.

**Secure configuration**: Review default configurations. Default settings are often optimized for convenience, not security. The CIS Benchmarks and cloud provider security baselines are good starting points.

## The Provider Models Are Similar

AWS, Azure, and GCP all publish their shared responsibility models. The specific language and diagrams differ, but the underlying concept is the same: the provider owns the infrastructure, the customer owns what they put on it and how they configure it.

AWS calls it the "Shared Responsibility Model" and has a clear diagram showing the line between "Security of the Cloud" (AWS) and "Security in the Cloud" (customer).

Azure frames it in terms of service type, with a table showing which responsibilities shift as you move from on-premises to IaaS to PaaS to SaaS.

GCP's model follows the same pattern. The specific services differ, but the principle doesn't.

The model doesn't eliminate the need for security expertise. If anything, it requires more expertise, because you need to understand both the security controls available in the cloud platform and how to apply them correctly. The cloud removes the operational burden of managing physical hardware; it doesn't remove the responsibility for securing your data and workloads.
