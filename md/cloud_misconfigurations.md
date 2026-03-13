# Common Cloud Misconfigurations

Cloud platforms make it genuinely easy to expose things accidentally. The same self-service model that lets a developer spin up a database in thirty seconds also lets that developer misconfigure it in thirty seconds. Security controls that would have required explicit action in a traditional data center are often opt-in in the cloud, which means the path of least resistance is frequently the insecure one. This is why misconfigurations, not sophisticated exploits, dominate cloud breach reports.

## Publicly Accessible Storage Buckets

The most iconic cloud misconfiguration. An S3 bucket (or Azure Blob Storage container, or GCS bucket) configured to allow public read access exposes everything in it to anyone on the internet without any authentication.

How it happens: a developer needs to share files publicly, applies a bucket policy that grants public access, and forgets to scope it appropriately. Or a default configuration from years ago persists. Or a deployment script sets broad permissions for convenience and nobody audits it afterward.

What researchers typically find in exposed buckets: database backups, application logs containing user data, configuration files with hardcoded credentials, internal documents, PII, healthcare data, financial records. The variety is impressive. People store everything in S3.

Tools for finding them: **S3Scanner** enumerates S3 bucket names and checks their permission settings. **GrayhatWarfare** is a searchable public database of known open buckets. Attackers use both.

Prevention is straightforward. AWS added an "S3 Block Public Access" setting at both the bucket and account level that prevents public access policies from taking effect regardless of what the bucket policy says. Enabling this at the account level is the correct default for organizations that don't need public buckets. Azure and GCP have equivalent controls. Enable them. Also audit existing bucket policies regularly; IAM permissions drift.

## Overpermissive IAM

Giving IAM principals more permissions than they need is the second most consequential cloud misconfiguration category.

The most egregious version: attaching the AWS `AdministratorAccess` policy (which grants `*:*` on `*` resources) to an application role, a developer user, or a CI/CD pipeline. This is convenience masquerading as configuration. If that credential is compromised, the attacker owns the entire AWS account.

Other common forms:

**Long-lived access keys committed to code**: AWS access keys in a GitHub repository, a Docker image, an S3 bucket, a Lambda environment variable. Tools like **truffleHog** and **git-secrets** scan for credential patterns in code repositories. Attackers run similar scans continuously on public repos. AWS itself monitors for its own keys on GitHub and proactively alerts, but you shouldn't rely on that.

**Root account usage**: The AWS root account has unrestricted access to everything and cannot be fully restricted by IAM policies. It should have a hardware MFA token attached and should essentially never be used for day-to-day operations. Many organizations have root accounts with no MFA and access keys created (which should never happen).

**No credential rotation**: IAM access keys that have existed for years, with no expiry, are a standing risk. Programmatic access should use short-lived credentials via IAM roles wherever possible, and long-lived keys should be rotated regularly and audited for last-use dates.

The principle of least privilege is clear in theory and hard to apply consistently in practice. A useful approach: start with no permissions and add only what's actually needed, rather than starting with broad permissions and trying to restrict.

## Exposed Instance Metadata Service

Every EC2 instance (and equivalent VM in Azure and GCP) has access to a metadata endpoint at `169.254.169.254`. This endpoint provides instance metadata, user data scripts, and, critically, temporary IAM credentials for any IAM role attached to the instance.

A request like this, made from the instance:

```
GET http://169.254.169.254/latest/meta-data/iam/security-credentials/my-role-name
```

Returns a JSON object containing an `AccessKeyId`, `SecretAccessKey`, and `Token` that are valid AWS credentials. Any process running on the instance can make this request.

**IMDSv1** requires no authentication. Any process (or HTTP request that gets proxied through a vulnerable application) can query the metadata service and retrieve credentials.

**IMDSv2** is session-oriented. Retrieving metadata requires first making a PUT request to get a session token, then using that token in the actual metadata request. This extra step breaks most SSRF-based metadata credential theft, because SSRF vulnerabilities typically allow GET requests but not PUT requests.

The Capital One breach is the best-documented example of SSRF plus IMDSv1 credential theft in the wild. The attacker exploited a WAF misconfiguration via SSRF, reached the metadata service, got IAM role credentials, and used those to access S3 buckets.

Mitigation: enforce IMDSv2 on all instances. AWS lets you do this at the account level and at the instance level. There's no good reason to leave IMDSv1 enabled.

## Security Group Misconfigurations

Security groups in AWS (and equivalent network security controls in Azure and GCP) act as virtual firewalls for individual instances and services. Misconfigured security groups are a reliable way to expose services directly to the internet.

The most dangerous pattern: an inbound rule allowing `0.0.0.0/0` (any IP) on port 22 (SSH), port 3389 (RDP), or any database port (3306 for MySQL, 5432 for PostgreSQL, 1433 for MSSQL, 27017 for MongoDB).

SSH and RDP open to the internet mean every credential-guessing bot and every vulnerability scanner on the internet can attempt to authenticate. Even with strong passwords, you're exposed to credential stuffing, brute force, and any SSH/RDP vulnerabilities that emerge.

Databases open to the internet are worse. Database services typically aren't designed to be internet-facing; authentication mechanisms can be weak, and there's no reason for a production database to accept connections from arbitrary source IPs.

Correct approach: the only IP that should reach an admin port is the specific IP or CIDR range of the admin's machine or a dedicated bastion host. Application ports (80, 443) can be open to the world; management ports shouldn't be.

## Publicly Exposed Databases

Related to the above, but worth calling out separately because of how often it happens. MongoDB, Elasticsearch, and Redis in particular have been found exposed on the public internet with no authentication at all, because earlier default configurations didn't require passwords and some administrators never changed that.

At various points researchers have found millions of MongoDB instances, hundreds of thousands of Elasticsearch clusters, and large numbers of Redis databases publicly accessible with no credentials. The data in these ranged from development environments with fake data to production systems with customer PII and financial records.

Prevention: databases should not have public IP addresses. They should be in private subnets, accessible only from application servers within the same VPC or through a VPN/bastion. Authentication should always be enabled, credentials should be strong, and network access should be restricted at the security group level regardless.

## Logging Disabled

CloudTrail in AWS records API calls across the account: who made what API call, from where, when, and what the response was. It's the primary source of audit logging for cloud account activity. Turning it off, or never turning it on, means you have no visibility into what's happening in your account.

The same applies to S3 server access logs (who accessed which objects), VPC flow logs (network traffic metadata), and CloudWatch Logs for applications.

Organizations that disable or never enable logging discover this problem during incident response when they need to reconstruct what an attacker did and find that the evidence doesn't exist. This is not a recoverable situation.

Logging doesn't prevent attacks, but it's the difference between investigating an incident and guessing about one. Enable CloudTrail in all regions. Enable S3 access logging on sensitive buckets. Enable VPC flow logs. Centralize logs in a separate account or export them somewhere the attacker can't reach.

## Secrets in Code and Environments

Hardcoded secrets in application code are a classic problem that the cloud makes more consequential because the secrets are often cloud provider credentials with broad permissions.

Patterns to look for and avoid:

**Hardcoded in source code**: AWS keys, database passwords, API tokens directly in code that gets committed to version control. Even if you later remove the secret from the file, it still exists in git history. Use `git-secrets` or similar pre-commit hooks to prevent this.

**In environment variables**: Passing secrets as environment variables in Docker containers or Lambda functions is better than hardcoding, but Lambda environment variables are visible in the AWS console to anyone with sufficient IAM access, and they can appear in logs if someone prints `os.environ`.

**In container images**: Building secrets into Docker images bakes them permanently into every layer of the image. Anyone who pulls the image has the secret.

**Better alternatives**: AWS Secrets Manager or AWS Parameter Store (with SecureString type) store secrets outside the application, with access controlled by IAM, audit logging, and optional automatic rotation. The application retrieves secrets at runtime. Similar services exist in Azure (Key Vault) and GCP (Secret Manager).

## Default VPC and Default Security Groups

Every AWS region has a default VPC that exists automatically. It comes with default subnets and a default security group. The default security group allows all inbound traffic from other resources also using the default security group, and all outbound traffic. This is a permissive default that many organizations never audit.

The correct practice: don't use the default VPC for production workloads. Create VPCs with intentional design: private subnets, public subnets, specific routing, specific security groups with explicit rules. The default VPC exists for quick experimentation; treat it as a scratch environment.

Similarly, the default security group should be restricted or a policy should be in place preventing resources from being attached to it.

## Tools for Finding Misconfigurations

**ScoutSuite**: Open source multi-cloud security auditing tool. Enumerates cloud resources and checks them against known security best practices. Generates reports organized by service.

**Prowler**: AWS-focused security assessment tool with hundreds of checks. Covers CIS Benchmarks, GDPR, HIPAA, PCI DSS, and other frameworks. Also has Azure and GCP support.

**Checkov**: Scans Infrastructure as Code (Terraform, CloudFormation, Kubernetes manifests) for security misconfigurations before deployment. Running this in CI/CD prevents misconfigurations from reaching production.

**AWS Trusted Advisor**: Built into the AWS console. Provides checks for security, cost, performance, and reliability. The security checks cover common issues like open security groups, no MFA on root, public S3 buckets, and exposed IAM access keys. Free tier covers the most important security checks.

**Microsoft Defender for Cloud** (formerly Azure Security Center): Cloud security posture management for Azure environments. Surfaces misconfigurations, tracks secure score, and provides remediation guidance.

Running these tools periodically against production environments is good hygiene. Running them as part of CI/CD for infrastructure changes is better. The goal is finding misconfigurations before attackers do.
