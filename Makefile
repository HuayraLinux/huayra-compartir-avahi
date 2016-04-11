VERSION=0.0.1
NOMBRE="huayra-compartir-avahi"

N=[0m
G=[01;32m
Y=[01;33m
B=[01;34m


comandos:
	@echo ""
	@echo "${B}Comandos disponibles para ${Y}${NOMBRE}${N} (versión: ${VERSION})"
	@echo ""
	@echo "  ${Y}Para desarrolladores${N}"
	@echo ""
	@echo "    ${G}version_patch${N}        Genera una nueva versión."
	@echo "    ${G}version_minor${N}        Genera una nueva versión."
	@echo "    ${G}subir_version${N}        Sube version generada al servidor."
	@echo ""

subir_version:
	@git commit -am 'release ${VERSION}'
	@git tag '${VERSION}'
	@git push
	@git push --all
	@git push --tags

version_patch:
	@bumpversion patch --current-version ${VERSION} Makefile --list
	@make _help_version

version_minor:
	@bumpversion minor --current-version ${VERSION} Makefile --list
	@make _help_version

_help_version:
	@echo "Esrecomendable escribir el comando que genera los tags y sube todo a github:"
	@echo ""
	@echo "make subir_version"
