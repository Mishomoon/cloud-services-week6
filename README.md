# Cloud Services – Week 6
## CI/CD & Observability

This project is the Week 6 continuation of the Cloud Services course project.

The application was developed step by step during Weeks 4, 5 and 6.
Week 6 focuses on CI/CD, automated container image building and
deployment, health probes, logging and observability.

---

# 1. Project Links

## Week 4 – Containerized Application

**Application:**

https://frontend-cloud-services-week4.2.rahtiapp.fi

**GitHub Repository:**

https://github.com/Mishomoon/cloud-services-week4

---

## Week 5 – Cloud Application

**Application:**

https://frontend-cloud-services-week5.2.rahtiapp.fi

**GitHub Repository:**

https://github.com/Mishomoon/cloud-services-week5

---

## Week 6 – CI/CD & Observability

**Application:**

https://frontend-cloud-services-week6.2.rahtiapp.fi

**GitHub Repository:**

https://github.com/Mishomoon/cloud-services-week6

**Rahti Project:**

`cloud-services-week6`

---

# 2. Project Overview

The project is a containerized web application deployed on the Rahti
OpenShift platform.

The application consists of several services:

- Nginx frontend
- Flask backend
- MySQL database
- Redis cache

The project was developed progressively:


Week 4
Containerized application
        |
        v
Week 5
Cloud deployment + MySQL + Redis
        |
        v
Week 6
CI/CD + health probes + logging + observability

Week 6 extends the previous application by adding an automated
CI/CD pipeline using GitHub Actions.

The pipeline builds Docker images, pushes them to GitHub Container
Registry (GHCR), connects to Rahti/OpenShift and updates the deployed
application.

3. Architecture

The application follows a three-tier architecture.

                         USER
                           |
                           v
                    +-------------+
                    |   Nginx     |
                    |  Frontend   |
                    +-------------+
                           |
                           v
                    +-------------+
                    |    Flask    |
                    |   Backend   |
                    +-------------+
                       /       \
                      /         \
                     v           v
              +----------+   +---------+
              |  MySQL   |   |  Redis  |
              | Database |   |  Cache  |
              +----------+   +---------+

The frontend communicates with the Flask backend.

The backend communicates with MySQL for persistent data and Redis for
caching.

The services run as separate containers in OpenShift.

4. Week 6 Goals

The main goals of Week 6 were:

Create a GitHub Actions CI/CD pipeline
Build Docker images automatically
Push Docker images to GitHub Container Registry
Deploy the application automatically to Rahti/OpenShift
Use commit SHA tags for container images
Add readiness probes
Add liveness probes
Test application health and recovery
Check deployment rollout status
Collect application logs
Demonstrate basic observability
Keep authentication information in GitHub Secrets
Document the deployment and troubleshooting process
5. GitHub Actions CI/CD

The CI/CD workflow is located at:

.github/workflows/week6.yml

The workflow is triggered when changes are pushed to the main
branch.

The general pipeline is:

Git Push
   |
   v
GitHub Actions
   |
   v
Checkout repository
   |
   v
Login to GHCR
   |
   v
Build backend image
   |
   v
Push backend image
   |
   v
Build frontend image
   |
   v
Push frontend image
   |
   v
Install OpenShift CLI
   |
   v
Login to Rahti
   |
   v
Select cloud-services-week6 project
   |
   v
Deploy backend
   |
   v
Deploy frontend
   |
   v
Check rollout
   |
   v
Restore frontend
6. GitHub Container Registry

The Docker images are stored in GitHub Container Registry (GHCR).

The workflow logs in to GHCR using the GitHub token.

The workflow uses package permissions so that GitHub Actions can push
the built images.

The workflow contains:

permissions:
  contents: read
  packages: write

The actual authentication token is not written directly into the
repository.

7. Backend Docker Image

The backend image is built from the backend directory.

Example command:

docker build -t "$BACKEND_IMAGE:${GITHUB_SHA}" ./backend

The image is then pushed to GHCR:

docker push "$BACKEND_IMAGE:${GITHUB_SHA}"

The image is tagged using the GitHub commit SHA.

This makes it possible to identify which source-code commit produced
the deployed image.

8. Frontend Docker Image

The frontend image is built from the frontend directory.

Example:

docker build -t "$FRONTEND_IMAGE:${GITHUB_SHA}" ./frontend

The image is then pushed to GHCR:

docker push "$FRONTEND_IMAGE:${GITHUB_SHA}"

The frontend image contains the Nginx configuration and frontend
application files.

9. Commit SHA Image Tags

The CI/CD pipeline uses the Git commit SHA as the image tag.

The deployment process is therefore:

Git commit
     |
     v
GitHub Actions
     |
     v
Docker build
     |
     v
Image tagged with commit SHA
     |
     v
Image pushed to GHCR
     |
     v
OpenShift deployment

For example:

backend:<commit-sha>
frontend:<commit-sha>

This makes the deployment traceable to a specific Git commit.

10. OpenShift / Rahti

The application is deployed to the Rahti OpenShift platform.

The Week 6 project is:

cloud-services-week6

The main deployments are:

frontend
backend
mysql
redis

The application can be checked with:

oc get pods -n cloud-services-week6

The expected result is that the application pods are running.

11. OpenShift Authentication

GitHub Actions connects to Rahti using the OpenShift CLI.

The workflow uses GitHub repository secrets.

The authentication information is not stored directly in the source
code.

The workflow uses values such as:

RAHTI_SERVER
RAHTI_TOKEN

The login command is:

oc login --server="${{ secrets.RAHTI_SERVER }}" \
  --token="${{ secrets.RAHTI_TOKEN }}"

The token is stored as a GitHub Secret.

It is not included in the README or source code.

12. Selecting the Week 6 Project

After logging into Rahti, the workflow selects the Week 6 project:

oc project cloud-services-week6

This ensures that the deployment commands are executed in the correct
OpenShift project.

13. CPU Resource Handling

The Rahti project has limited CPU resources.

During deployment, the frontend can temporarily be scaled down so that
there is enough available CPU for the backend deployment.

The frontend can be scaled down with:

oc scale deployment/frontend \
  --replicas=0 \
  -n cloud-services-week6

After the backend deployment, the frontend is restored:

oc scale deployment/frontend \
  --replicas=1 \
  -n cloud-services-week6

The pipeline also waits for the deployment to finish.

This helps the CI/CD pipeline work within the available OpenShift
resource limits.

14. Backend Deployment

The backend deployment is updated with the new container image.

Example:

oc set image deployment/backend \
  backend="$BACKEND_IMAGE:${GITHUB_SHA}" \
  -n cloud-services-week6

The workflow then checks the rollout:

oc rollout status deployment/backend \
  -n cloud-services-week6 \
  --timeout=180s

This allows the workflow to detect whether the backend deployment
completed successfully.

15. Frontend Deployment

The frontend deployment is updated with the newly built image.

Example:

oc set image deployment/frontend \
  frontend="$FRONTEND_IMAGE:${GITHUB_SHA}" \
  -n cloud-services-week6

The frontend is then restored to one replica:

oc scale deployment/frontend \
  --replicas=1 \
  -n cloud-services-week6

The workflow waits for the frontend rollout to complete.

16. Readiness Probe

A readiness probe checks whether an application is ready to receive
traffic.

The backend uses a health endpoint for the probe.

Example configuration:

readinessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 10
  periodSeconds: 10

The readiness probe prevents traffic from being sent to a pod that is
not ready.

When the application becomes ready, the pod can receive traffic through
the Service.

17. Liveness Probe

A liveness probe checks whether the application is still functioning.

Example:

livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 20
  periodSeconds: 10

If the application becomes unhealthy and repeatedly fails the liveness
check, OpenShift can restart the container.

This provides automatic recovery for certain application failures.

18. Probe Testing

The Week 6 work includes testing the health probes.

The application was tested in both healthy and unhealthy states.

The general behaviour is:

Application healthy
       |
       v
Health check succeeds
       |
       v
Pod remains ready

If the application becomes unhealthy:

Application failure
       |
       v
Health check fails
       |
       v
OpenShift detects the failure
       |
       v
Container can be restarted/recovered

The repository contains screenshots showing the probe configuration
and the testing process.

19. Application Logs

OpenShift logs can be viewed with:

oc logs <pod-name> -n cloud-services-week6

The logs provide information about application requests and health
checks.

The logging evidence includes backend logs and health-check requests.

Logs are useful for:

Troubleshooting
Checking application requests
Checking HTTP responses
Investigating deployment problems
Understanding application behaviour
20. Rollout Verification

The deployment rollout can be checked using:

oc rollout status deployment/backend \
  -n cloud-services-week6

and:

oc rollout status deployment/frontend \
  -n cloud-services-week6

A successful rollout means that OpenShift successfully updated the
deployment and the required pods became ready.

21. Pod Verification

The deployed pods can be checked with:

oc get pods -n cloud-services-week6

The Week 6 environment contains:

backend
frontend
mysql
redis

The goal is for the required pods to show a healthy and ready status.

22. Observability

Week 6 introduces several basic observability methods.

Health

Readiness and liveness probes provide information about application
health.

Logs

Application logs provide information about requests and application
behaviour.

Pods

OpenShift pod status shows whether containers are running.

Rollouts

Rollout status shows whether a new deployment completed successfully.

Together these provide basic visibility into the state of the
application.

23. Alerting

The health and logging information can also be used as the basis for
alerts.

Possible alerts include:

Repeated readiness probe failures
Repeated liveness probe failures
Repeated pod restarts
Failed deployments
Increased HTTP 5xx responses

For example:

Alert when the backend readiness probe continuously
fails for several minutes.

Another possible alert is:

Alert when the backend produces an unusual number
of HTTP 5xx responses.

These types of alerts can help identify application problems early.

24. Security

Sensitive authentication information is not included in the repository.

The Rahti authentication token is stored as a GitHub Secret.

The project does not intentionally expose:

Rahti authentication tokens
Passwords
Private keys
Database credentials
SSH credentials

The README also does not contain any secret values.

25. Troubleshooting During Week 6

Several problems were encountered during the development of the Week 6
CI/CD pipeline.

OpenShift CLI not found

One pipeline attempt produced:

oc: command not found

The workflow was updated to install the OpenShift CLI using:

- name: Install OpenShift CLI
  uses: redhat-actions/oc-installer@v1
OpenShift Configuration Error

Another pipeline attempt produced an error saying that OpenShift
configuration information was missing.

The problem was related to the OpenShift login/configuration.

The pipeline was updated so that it logs into Rahti before running
OpenShift commands.

Expired Rahti Token

Another attempt failed because the Rahti token was invalid or expired.

The GitHub Secret containing the Rahti token was updated.

After updating the token, GitHub Actions could authenticate to Rahti
again.

GHCR Package Permissions

The frontend image push initially failed because GitHub Actions did
not have the required package permissions.

The workflow was configured with:

permissions:
  contents: read
  packages: write

This allows GitHub Actions to push container images to GHCR.

CPU Resource Limitation

The project also encountered CPU resource limitations in the Rahti
project.

The pipeline handles this by temporarily scaling down the frontend
during deployment and restoring it afterwards.

26. Repository Structure
cloud-services-week6/
│
├── .github/
│   └── workflows/
│       └── week6.yml
│
├── backend/
│   ├── Dockerfile
│   └── application files
│
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── index.html
│   └── screenshots-week6/
│
├── rahti/
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── mysql-deployment.yaml
│   └── redis-deployment.yaml
│
├── docker-compose.dev.yml
├── docker-compose.prod.yml
└── README.md
27. Week 6 Evidence

The frontend/screenshots-week6/ directory contains screenshots used
as evidence for the Week 6 implementation and testing.

The evidence includes:

GitHub Actions workflow
CI/CD configuration
Git commit SHA
Backend rollout
Backend pod running
Final pods
OpenShift route
Frontend deployment
Backend deployment
Readiness probe
Liveness probe
Probe testing
Recovery testing
Backend Service endpoints
Backend logs
Health-check logs
Route and image information
TLS route information

These screenshots document the configuration and testing performed
during the assignment.

28. Development Progress

The project was developed progressively throughout the course.

Week 4

The application was containerized and deployed.

Application:

https://frontend-cloud-services-week4.2.rahtiapp.fi

Repository:

https://github.com/Mishomoon/cloud-services-week4

Week 5

The application was extended with cloud deployment and database/cache
functionality.

Application:

https://frontend-cloud-services-week5.2.rahtiapp.fi

Repository:

https://github.com/Mishomoon/cloud-services-week5

Week 6

The application was extended with CI/CD and observability.

Repository:

https://github.com/Mishomoon/cloud-services-week6

Rahti project:

cloud-services-week6

The Week 6 application URL is provided at the top of this README.

29. Final Result

The Week 6 project demonstrates an automated deployment workflow for a
containerized application.

The main workflow is:

Developer pushes code
        |
        v
GitHub repository
        |
        v
GitHub Actions
        |
        +-------------------+
        |                   |
        v                   v
Build backend        Build frontend
        |                   |
        v                   v
Push to GHCR         Push to GHCR
        |                   |
        +---------+---------+
                  |
                  v
          Login to Rahti
                  |
                  v
       Select Week 6 project
                  |
                  v
        Update OpenShift
          deployments
                  |
                  v
          Rollout checks
                  |
                  v
       Health probe checks
                  |
                  v
       Application running

The project demonstrates the use of GitHub Actions, Docker, GitHub
Container Registry and OpenShift/Rahti together to automate the build
and deployment process.

30. Conclusion

Week 6 builds on the containerized application created during Weeks 4
and 5.

The main focus of Week 6 is automation and observability.

The GitHub Actions pipeline automatically builds and pushes the
frontend and backend container images and deploys them to the Rahti
OpenShift environment.

Readiness and liveness probes provide application health checks, while
OpenShift logs, pod status and rollout status provide information about
the running application and deployment process.

The project therefore demonstrates a complete workflow from source-code
commit to container image creation, registry storage, OpenShift
deployment and application health monitoring.
