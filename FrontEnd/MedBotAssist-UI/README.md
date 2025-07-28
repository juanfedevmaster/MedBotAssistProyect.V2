# MedBotAssist UI

MedBotAssist es una aplicación diseñada para ayudar a los usuarios a gestionar sus necesidades de salud mediante un asistente virtual. Esta interfaz de usuario está construida con React 18 y TypeScript.

## Estructura del Proyecto

El proyecto tiene la siguiente estructura de archivos:

```
MedBotAssist-UI
├── src
│   ├── App.tsx                # Componente principal que maneja las rutas
│   ├── index.tsx              # Punto de entrada de la aplicación
│   ├── config
│   │   └── endpoints.ts       # Configuración de los endpoints de la API
│   ├── modules
│   │   └── login
│   │       ├── Login.tsx      # Componente de inicio de sesión
│   │       └── Login.module.css# Estilos para el componente de inicio de sesión
│   ├── pages
│   │   └── Home.tsx           # Página principal de la aplicación
│   └── types
│       └── index.ts           # Tipos e interfaces utilizados en la aplicación
├── package.json                # Configuración de npm y dependencias
├── tsconfig.json              # Configuración de TypeScript
└── README.md                  # Documentación del proyecto
```

## Instalación

Para instalar las dependencias del proyecto, ejecuta el siguiente comando en la raíz del proyecto:

```
npm install
```

## Ejecución

Para iniciar la aplicación en modo de desarrollo, utiliza el siguiente comando:

```
npm start
```

Esto abrirá la aplicación en tu navegador predeterminado.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o un pull request en el repositorio.

## Licencia

Este proyecto está bajo la Licencia MIT.

## Solución de problemas comunes

### Error: "Patient ID not found or user not authenticated" en /patients/notes/:id

Este error puede ocurrir cuando navegas directamente a la URL de notas del paciente. Esto se debe a que la aplicación necesita verificar tu autenticación primero.

**Solución:**
1. Asegúrate de estar logueado antes de navegar a las notas
2. Si ya estás logueado, ve primero a la página de pacientes (`/patients`)
3. Luego navega al detalle del paciente (`/patients/view/:id`)
4. Finalmente usa el botón "Add Note" para acceder a las notas

**Nota técnica:** La aplicación ahora verifica automáticamente la autenticación almacenada al cargar, pero es recomendable seguir el flujo de navegación normal.

## Para refrescar el proceso en el puerto 3000 usa

netstat -ano | findstr :3000
taskkill /PID {LISTENING} /F