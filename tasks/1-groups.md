Paso 1: Registro del grupo

Este primer paso sirve para registrar vuestro grupo y dejar trazabilidad en GitHub de quiénes sois y qué dataset vais a usar.

⸻

1) Hacer un fork del repositorio
	1.	Entrad en el repositorio de la asignatura.
	2.	Pulsad Fork (arriba a la derecha) para crear una copia en vuestra cuenta.
	3.	En vuestro fork, comprobad que estáis en la rama principal (main o master, según el repo).

⸻

2) Clonar vuestro fork en local

En vuestro ordenador:

git clone https://github.com/<vuestro-usuario>/sw-kg.git
cd <repo>

(Opcional, pero recomendado) Añadid el repositorio original como upstream para poder actualizar cambios:

git remote add upstream https://github.com/usc-gria/sw-kg.git
git fetch upstream


⸻

3) Crear una carpeta para el grupo

Regla de nombre de la carpeta

El nombre de la carpeta se construye así:
	•	Por cada integrante, tomad las dos primeras letras de cada apellido (en minúsculas).
	•	Concatenadlo todo en el mismo orden en el que aparecéis en la lista de miembros.

Ejemplo:
	•	Integrante 1: Ana García López → ga 
	•	Integrante 2: Mario Pérez Díaz → pe
	•	Carpeta del grupo: gape

Crear la carpeta

En el repositorio, cread una carpeta dentro de teams/. Por defecto:

groups/<nombre_carpeta>/

Por ejemplo:

groups/gape/


⸻

4) Añadir el archivo template_groups.yaml dentro de la carpeta

Dentro de vuestra carpeta de grupo, cread info.yaml usando esta plantilla mínima:

⸻

5) Hacer commit de los cambios:

Añadid y confirmad:

git add .
git commit -m "Add group info <nombre_grupo>"


⸻

6) Subir la rama a vuestro fork

git push


⸻

7) Abrir un Pull Request (PR) hacia el repositorio original
	1.	En GitHub, id a vuestro fork.
	2.	Veréis un botón para Compare & pull request (o creadlo desde Pull requests).
	4.	Título recomendado del PR: [Step1] Add group <nombre_carpeta>

⸻

Checklist antes de enviar el PR
	•	Carpeta creada con el nombre correcto.
	•	info.yaml dentro de la carpeta.
	•	Enlace al dataset funciona.
	•	PR abierto correctamente al repositorio original.