```markdown
## Development Mode

The project supports a development mode for running the environment with Docker Compose. This includes options for building the containers, running in standard mode, and debugging.

### Makefile Commands

#### **1. Start Development**
Start the Docker Compose environment using the default configuration:
```bash
make start-development
```

This command runs `docker-compose up` with the default settings from `docker-compose.yml`.

#### **2. Start Development with Build**
If you need to rebuild the containers before starting them, use the `BUILD=1` flag:
```bash
make start-development BUILD=1
```

This command forces a rebuild of the containers by running `docker-compose up --build`.

#### **3. Start Development in Debug Mode**
For debugging, use the `DEBUG=1` flag:
```bash
make start-development DEBUG=1
```

This command runs `docker-compose` with both the `docker-compose.yml` and `docker-compose.override.yml` files. The override file includes the following configuration:
```yaml
command: tail -f /dev/null
```

This allows the container to remain running without executing the application, so you can attach to it and debug manually.

#### **4. Stop Development**
Stop the Docker Compose environment:
```bash
make stop-development
```

This command stops and removes all containers, networks, and volumes created by Docker Compose.

---

### Debugging

In debug mode, the container uses the `command: tail -f /dev/null` to keep it running without starting the application. This allows you to manually execute commands inside the container. To attach to the container:
```bash
docker exec -it <container_name> bash
```

Replace `<container_name>` with the actual name of the container.

---

### Notes

- Ensure Docker and Docker Compose are installed and running on your system.
- Use the `docker-compose.override.yml` file only for debugging.
- In standard mode, the application runs as defined in the `Dockerfile`.
```