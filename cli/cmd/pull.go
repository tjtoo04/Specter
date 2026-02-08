package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

var pullCmd = &cobra.Command{
	Use:   "pull [project_id]",
	Short: "Pull project configuration from FastAPI",
	Args:  cobra.ExactArgs(1), // Ensures user provides the ID
	Run: func(cmd *cobra.Command, args []string) {
		projectID := args[0]
		fmt.Printf("Fetching config for project: %s...\n", projectID)

		// 1. Load auth token from local storage
		// 2. http.Get("http://localhost:8000/api/configurations/project/" + projectID)
		//    Note: Add "Authorization: Bearer <token>" header
		// 3. Save response JSON to .specter/config.yaml in the current directory

		fmt.Println("Configuration saved locally.")
	},
}

func init() {
	rootCmd.AddCommand(pullCmd)
}
