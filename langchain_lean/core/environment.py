import logging
import os
import shutil
from pathlib import Path

import docker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("langchain-lean-env")


class LeanEnvironmentManager:
    """Gestiona Docker y los volúmenes persistentes para ejecutar Lean 4."""

    def __init__(
        self,
        image_name: str = "langchain-lean:lean4-v4.11.0",
        fallback_image: str = "leanprover/lean4:v4.11.0",
        workspace_path: str = "./lean_workspace",
        cache_path: str | None = None,
    ):
        self.image_name = image_name
        self.fallback_image = fallback_image
        self.runtime_image = image_name
        self.workspace_path = os.path.abspath(workspace_path)
        default_cache = os.path.join(Path.home(), ".cache", "langchain-lean")
        self.cache_path = os.path.abspath(cache_path or default_cache)

        try:
            self.client = docker.from_env()
        except docker.errors.DockerException as exc:
            raise RuntimeError(
                "No se pudo conectar con Docker. Verifica que Docker esté instalado y en ejecución."
            ) from exc

    def provision_environment(self) -> None:
        logger.info("Verificando entorno Lean...")
        self._ensure_workspace_exists()
        self._ensure_cache_exists()
        self._ensure_image_is_ready()
        logger.info("Entorno Lean listo.")

    def _ensure_workspace_exists(self) -> None:
        os.makedirs(self.workspace_path, exist_ok=True)
        lakefile = os.path.join(self.workspace_path, "lakefile.lean")
        if not os.path.exists(lakefile):
            with open(lakefile, "w", encoding="utf-8") as file:
                file.write('import Lake\nopen Lake DSL\npackage "langchain_lean_workspace" {}\n')
            logger.info("Workspace Lean inicializado en %s", self.workspace_path)

    def _ensure_cache_exists(self) -> None:
        os.makedirs(self.cache_path, exist_ok=True)
        os.makedirs(os.path.join(self.cache_path, ".cache"), exist_ok=True)

    def _ensure_image_is_ready(self) -> None:
        try:
            self.client.images.get(self.image_name)
            self.runtime_image = self.image_name
            logger.info("Imagen local encontrada: %s", self.image_name)
            if self._image_has_lake(self.runtime_image):
                return
            logger.warning("La imagen %s no incluye lake. Intentando fallback...", self.image_name)
        except docker.errors.ImageNotFound:
            pass

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        docker_dir = os.path.join(base_dir, "Docker")
        dockerfile = os.path.join(docker_dir, "Dockerfile")

        if os.path.exists(dockerfile):
            try:
                logger.info("Construyendo imagen local %s desde %s", self.image_name, docker_dir)
                self.client.images.build(path=docker_dir, tag=self.image_name, rm=True)
                self.runtime_image = self.image_name
                if self._image_has_lake(self.runtime_image):
                    return
                logger.warning("La imagen recién construida no incluye lake. Usando fallback.")
            except Exception as exc:  # pragma: no cover
                logger.warning("Build local falló: %s", exc)

        logger.info("Usando imagen fallback: %s", self.fallback_image)
        self.client.images.pull(self.fallback_image)
        self.runtime_image = self.fallback_image

    def _image_has_lake(self, image_name: str) -> bool:
        """Valida si la imagen provee lake en PATH."""
        try:
            output = self.client.containers.run(
                image_name,
                command="bash -lc 'command -v lake'",
                remove=True,
                stderr=True,
                stdout=True,
            )
            return bool(output.decode("utf-8", errors="replace").strip())
        except Exception:
            return False

    def run_command_in_container(self, command: str, timeout: int = 180) -> tuple[int, str]:
        """Ejecuta un comando en un contenedor efímero con caché persistente."""
        volumes = {
            self.workspace_path: {"bind": "/workspace", "mode": "rw"},
            os.path.join(self.cache_path, ".cache"): {"bind": "/root/.cache", "mode": "rw"},
        }

        container = None
        try:
            container = self.client.containers.run(
                self.runtime_image,
                command=f"bash -lc '{command}'",
                volumes=volumes,
                working_dir="/workspace",
                detach=True,
                remove=False,
                stdout=True,
                stderr=True,
            )
            result = container.wait(timeout=timeout)
            output = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")
            exit_code = int(result.get("StatusCode", 1))
            return exit_code, output
        except Exception as exc:
            return -1, f"Error Docker: {exc}"
        finally:
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

    def get_workspace_abs_path(self) -> str:
        return self.workspace_path

    def cleanup_workspace(self) -> None:
        if os.path.exists(self.workspace_path):
            shutil.rmtree(self.workspace_path)
