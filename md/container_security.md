# Container Security Basics

Containers changed how software gets deployed. They also changed the attack surface. The security model is different enough from traditional VMs that people with VM security experience often have gaps when they start working with containerized environments. This covers the key concepts: what makes containers different, where the risks are, and how to think about securing them.

## What Containers Actually Are

A container is an isolated group of processes running on a host, sharing the host's kernel. This is the critical distinction from a VM: a VM runs an entire separate operating system on top of a hypervisor, with its own kernel. A container uses the host kernel directly, relying on Linux namespaces and cgroups to create the illusion of isolation.

Namespaces provide isolation for process IDs, network interfaces, mount points, user IDs, and more. Cgroups limit resource usage (CPU, memory, I/O). Together they create an environment where processes think they're alone on a system and can't (in theory) see or interfere with each other or the host.

Docker is the most common container runtime, though Kubernetes environments often use containerd or CRI-O directly. The security properties are similar regardless of runtime.

## The Container Attack Surface

The main categories of container security risk:

**Container escape**: A technique by which an attacker, having compromised a process inside a container, gains access to the host or other containers. This is the most serious outcome.

**Vulnerable container images**: Container images are often built from base images that contain OS packages and libraries. Those packages have CVEs. Running containers built on unpatched base images is running vulnerable software.

**Misconfigured runtime**: Running containers with capabilities, privileges, or volume mounts they don't need dramatically expands the attack surface.

**Supply chain**: Pulling images from public registries without verification. Malicious or compromised images exist on Docker Hub.

## Privileged Containers

The `--privileged` flag is one of the most dangerous options you can give to a container. It disables essentially all the isolation mechanisms: the container gets access to all host devices, all Linux capabilities, and an unrestricted view of the host filesystem via `/dev`. Escaping a privileged container is trivial.

One classic escape: a privileged container can mount the host's root filesystem and write to it directly.

```bash
# Inside a privileged container
mkdir /mnt/host
mount /dev/sda1 /mnt/host
# Now /mnt/host is the host root filesystem
# Write a cron job, add an SSH key, modify any file
```

Privileged containers have legitimate uses, mostly for security tooling that needs to monitor the host and for some low-level system utilities. They should never be used for application workloads. If something only works with `--privileged`, that's a sign to investigate why it needs that before deploying it.

## Linux Capabilities

Rather than a binary privilege model (root vs not root), Linux splits root's powers into discrete capabilities. `CAP_NET_ADMIN` lets a process configure network interfaces. `CAP_SYS_PTRACE` lets it trace other processes. `CAP_SYS_ADMIN` is the kitchen sink: it grants so many privileges that it's functionally close to full root access.

Docker containers run with a reduced set of capabilities by default, but still more than most applications need. The correct approach is to drop everything and add back only what's specifically required:

```dockerfile
# In a Dockerfile or docker-compose
# Or at runtime:
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE myapp
```

`NET_BIND_SERVICE` is the most commonly needed capability: it allows binding to ports below 1024. Most web applications don't need anything else. Applications that don't need any special privileges should run with `--cap-drop=ALL` and nothing added back.

## Container Escape Techniques

**Privileged mode escape**: As described above. Mount the host filesystem, read sensitive files, write persistence mechanisms.

**Mounting the host Docker socket**: If `/var/run/docker.sock` is mounted into a container, that container has full Docker API access. It can spawn new privileged containers that mount the host filesystem, which is effectively the same as having root on the host. This is a common mistake in CI/CD pipelines where the build container needs to build Docker images.

```bash
# If the Docker socket is mounted, this is trivial
docker run -v /:/mnt --privileged alpine chroot /mnt sh
# Now you have a shell with the host filesystem as root
```

**Container runtime CVEs**: The container runtime itself can have vulnerabilities. CVE-2019-5736 (runc) allowed a malicious container to overwrite the runc binary on the host, leading to host code execution. The container runtime is a privileged process on the host; vulnerabilities in it are serious. Keep the runtime patched.

**Kernel exploits**: Because containers share the host kernel, kernel vulnerabilities can potentially be exploited from within a container to escape to the host. This is why running containers on up-to-date kernels matters.

## Image Security

Container images accumulate technical debt fast. A base image from two years ago has hundreds of unpatched CVEs. Images that include a full OS with package managers, compilers, and debugging tools have a much larger attack surface than minimal images.

**Don't use `:latest` tags**: The `latest` tag is mutable. The image it points to changes over time. Using a specific digest (`:sha256:abc123...`) pins you to an exact, verified image. At minimum, use a specific version tag; using digest hashes is better for production.

**Scan images for CVEs**: Tools like **Trivy**, **Grype**, and **Snyk Container** scan images against vulnerability databases. Running these in CI/CD, before images are deployed, catches known vulnerabilities before they reach production.

```bash
# Trivy example
trivy image myapp:1.2.3

# Grype example
grype myapp:1.2.3
```

**Use minimal base images**: Alpine Linux is 5MB and has a small package footprint. **Distroless** images (from Google) contain only the application runtime and its dependencies, with no shell, package manager, or OS utilities. Distroless images are hard to exploit interactively because there's no shell to get to even if you do find a path inside.

**Don't run as root**: Add a `USER` directive in your Dockerfile to switch to a non-root user before the final `CMD` or `ENTRYPOINT`. If an attacker compromises the process and the process is running as root inside the container, they have more options than if it's running as a regular user.

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
CMD ["node", "server.js"]
```

## Secrets Management

Baking secrets into container images is a hard antipattern to avoid in practice because it's convenient. It's also wrong.

**Why not in the image**: Every layer of a Docker image is stored and can be inspected. `docker history` shows all layers. Secrets committed to an image layer persist even if you `RUN unset SECRET` in a later layer. Anyone who can pull the image has the secret.

**Why not always as environment variables**: Environment variables are visible to all processes inside the container, can appear in logs and error dumps, and are visible in the Docker inspect output to anyone with Docker daemon access. They're better than hardcoding in images, but still not ideal for production sensitive credentials.

**Better alternatives**: For Kubernetes environments, use Secrets objects (which are a step up from ConfigMaps but not encrypted at rest by default unless you configure it). Better still: an external secrets manager like HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault. The application retrieves the secret at runtime, the secret is never baked in, access is audited, and rotation is possible without rebuilding images.

## Kubernetes-Specific Concerns

Kubernetes introduces additional security considerations beyond just running containers.

**RBAC misconfigurations**: Kubernetes RBAC controls what API operations each service account and user can perform. Overpermissive RBAC (wildcard verbs, cluster-admin grants, binding to the `cluster-admin` ClusterRole) is the Kubernetes equivalent of IAM over-permissioning.

**Exposed API server**: The Kubernetes API server should not be publicly accessible. Authenticate with strong credentials, restrict network access, enable audit logging.

**Default service account tokens**: Every pod by default gets a service account token mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token`. In older Kubernetes versions this token has more permissions than it should. Set `automountServiceAccountToken: false` for pods that don't need API access.

**Network policies**: By default, all pods in a Kubernetes cluster can communicate with all other pods. Network policies (similar to security groups but for pods) restrict this. Without them, a compromised pod can reach every other pod.

**Privileged pods**: The Pod Security Standards (which replaced PodSecurityPolicies in Kubernetes 1.25+) control whether pods can run as privileged, run as root, use host networking, etc. Enforce a restricted policy in production.

## Runtime Security

Even with good image scanning and capability restrictions, something unexpected can happen at runtime. Runtime security tools monitor container behavior and alert on anomalous activity.

**Seccomp profiles**: Restrict which system calls a container can make. Docker has a default seccomp profile that blocks around 40 system calls. A custom profile for a specific application can be much more restrictive. If a container gets exploited and an attacker tries to call `ptrace` or `mount`, a seccomp profile can block it.

**AppArmor and SELinux**: Mandatory access control systems that enforce policies on what files and resources a process can access. Docker supports both. AppArmor is more common on Ubuntu/Debian systems; SELinux is standard on RHEL/Fedora.

**Falco**: An open source runtime security tool by Sysdig that monitors syscall activity and generates alerts based on behavioral rules. Rules like "a shell was spawned inside a container" or "a container is reading /etc/shadow" or "an unexpected outbound connection was made from a production container" are detectable with Falco. It's effectively an IDS for container runtime behavior.

## The Image Supply Chain

Pulling a public image from Docker Hub and running it in production is trusting that image's entire build chain. Malicious base images have appeared on Docker Hub; even legitimate images can have compromised build processes.

Practices that reduce supply chain risk:

**Use trusted base images**: Prefer official images (marked with the verified badge) and well-maintained organization images over random community contributions.

**Pin to digests**: A tag like `node:18-alpine` can change. A digest like `node@sha256:abc123...` cannot.

**Scan in CI**: Every image built by your CI pipeline should be scanned for CVEs before it's pushed to your registry.

**Sign images**: Docker Content Trust and Sigstore/cosign allow signing container images and verifying signatures before running them. This proves the image came from a trusted build process and hasn't been tampered with.

**Private registry**: Push images to your own registry (Amazon ECR, Google Artifact Registry, Azure Container Registry, or self-hosted Harbor) rather than running directly from Docker Hub. This gives you control over what's available and a full audit log.

The container security landscape is deep. Getting the basics right (no privileged containers, minimal capabilities, regular image scanning, non-root processes, no secrets in images) covers the most impactful risks. From there, runtime monitoring and supply chain controls are the natural next layer.
