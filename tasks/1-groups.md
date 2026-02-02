# Paso 1: Registro del grupo

Este primer paso sirve para registrar vuestro grupo y dejar trazabilidad en GitHub de quiénes sois y qué dataset vais a usar.

⸻

## Hacer un fork del repositorio
	1.	Entrad en el repositorio de la asignatura.
	2.	Pulsad Fork (arriba a la derecha) para crear una copia en vuestra cuenta.
	3.	En vuestro fork, comprobad que estáis en la rama principal (main o master, según el repo).

⸻

## Clonar vuestro fork en local

En vuestro ordenador:
```bash
git clone https://github.com/<vuestro-usuario>/sw-kg.git
cd <repo>
```

⸻

## Crear una carpeta para el grupo

Regla de nombre de la carpeta

El nombre de la carpeta se construye así:
* Por cada integrante, tomad las dos primeras letras del primer apellido (en minúsculas).
* Concatenadlo todo en el mismo orden en el que aparecéis en la lista de miembros (alfabético).

Ejemplo:
* Integrante 1: Ana García López → ga 
* Integrante 2: Mario Pérez Díaz → pe 
* Carpeta del grupo: gape

Crear la carpeta

En el repositorio, cread una carpeta dentro de teams/. Por defecto:

groups/[nombre_grupo]/

Por ejemplo:

groups/gape/


⸻

## Añadir el archivo template_groups.yaml dentro de la carpeta

Dentro de vuestra carpeta de grupo, cread info.yaml usando la plantilla que se encuentra en la carpeta raíz del repositorio.

⸻

## Hacer commit de los cambios:

Añadid y confirmad:

```bash
git add .
git commit -m "Add group info [nombre_grupo]"
``

⸻

## Subir la rama a vuestro fork
```bash
git push
```

⸻

## Abrir un Pull Request (PR) hacia el repositorio original
	1.	En GitHub, id a vuestro fork.
	2.	Veréis un botón para Compare & pull request (o creadlo desde Pull requests).
	4.	Título recomendado del PR: [Step1] Add group <nombre_carpeta>

⸻

Checklist antes de enviar el PR
	•	Carpeta creada con el nombre correcto.
	•	info.yaml dentro de la carpeta.
	•	Enlace al dataset funciona.
	•	PR abierto correctamente al repositorio original.