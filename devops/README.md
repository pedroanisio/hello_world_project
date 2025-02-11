```
docker compose --env-file devops/.env.dev -f devops/docker-compose.dev.yml up --build -d
```

```
docker compose --env-file devops/.env.dev -f devops/docker-compose.dev.yml exec web bash
```

```
