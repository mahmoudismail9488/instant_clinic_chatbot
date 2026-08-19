# Deploy API to AWS

Recommended for hackathon: **AWS App Runner** from the root `Dockerfile`.  
Alternative: **ECS Fargate** using [`../../deploy/aws/ecs-task-definition.json`](../../deploy/aws/ecs-task-definition.json).

## What the container includes

- Python 3.12 + `uv sync` dependencies  
- `backend/` application  
- Prebuilt `data/index/` (471 chunks, cfgB)  
- Healthcheck on `GET /health`  
- Entrypoint: `uv run clinic-api` (port **8000**)

## Build & push (ECR)

```bash
AWS_REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REPO=glucorag-api

aws ecr create-repository --repository-name $REPO --region $AWS_REGION || true
aws ecr get-login-password --region $AWS_REGION \
  | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

docker build -t $REPO:latest .
docker tag $REPO:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO:latest
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO:latest
```

## App Runner

1. Create service → Container registry → ECR image above.  
2. Port **8000**.  
3. Health check path `/health`.  
4. Environment:

| Key | Example |
|---|---|
| `GROQ_API_KEY` | from Secrets Manager / App Runner secrets |
| `CORS_ORIGINS` | `https://your-app.vercel.app` |
| `CORS_ORIGIN_REGEX` | `https://.*\.vercel\.app` |
| `API_WORKERS` | `1` (raise only if memory allows; embedder is heavy) |

5. Instance: ≥ **1 vCPU / 2 GB** (embeddings + numpy index).

## ECS Fargate

- Task definition template: `deploy/aws/ecs-task-definition.json`  
- Service behind an ALB, target group health check `/health`  
- Store `GROQ_API_KEY` in Secrets Manager  

## Local Docker smoke

```bash
docker compose up --build
curl -s http://localhost:8000/health | jq
```

## Scalability notes

- Index + LLM client load **once per worker** (`AppState` lifespan).  
- Horizontal scale: more App Runner / ECS tasks (stateless API).  
- For larger corpora later: move vectors to OpenSearch / Qdrant and keep API thin.  
- Do **not** set high `API_WORKERS` on small instances — each worker loads embeddings.
