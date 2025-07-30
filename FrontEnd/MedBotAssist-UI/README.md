# MedBotAssist UI

MedBotAssist is an application designed to help users manage their health needs through a virtual assistant. This user interface is built with React 18 and TypeScript.

## Project Structure

The project has the following file structure:

```
MedBotAssist-UI
├── src
│   ├── App.tsx                # Main component that handles routes
│   ├── index.tsx              # Application entry point
│   ├── config
│   │   └── endpoints.ts       # API endpoints configuration
│   ├── modules
│   │   └── login
│   │       ├── Login.tsx      # Login component
│   │       └── Login.module.css# Styles for the login component
│   ├── pages
│   │   └── Home.tsx           # Main application page
│   └── types
│       └── index.ts           # Types and interfaces used in the application
├── package.json                # npm configuration and dependencies
├── tsconfig.json              # TypeScript configuration
└── README.md                  # Project documentation
```

## Installation

To install the project dependencies, run the following command in the project root:

```
npm install
```

## Execution

To start the application in development mode, use the following command:

```
npm start
```

This will open the application in your default browser.

## Contributions

Contributions are welcome. If you wish to contribute, please open an issue or a pull request in the repository.

## License

This project is licensed under the MIT License.

## Common Troubleshooting

### Error: "Patient ID not found or user not authenticated" in /patients/notes/:id

This error may occur when you navigate directly to the patient notes URL. This is because the application needs to verify your authentication first.

**Solution:**
1. Make sure you are logged in before navigating to notes
2. If you are already logged in, go first to the patients page (`/patients`)
3. Then navigate to the patient detail (`/patients/view/:id`)
4. Finally use the "Add Note" button to access notes

**Technical note:** The application now automatically verifies stored authentication when loading, but it is recommended to follow the normal navigation flow.

## To refresh the process on port 3000 use

netstat -ano | findstr :3000
taskkill /PID {LISTENING} /F