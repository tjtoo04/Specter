package cmd

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"

	"github.com/spf13/cobra"
)

var pullCmd = &cobra.Command{
	Use:   "pull [project_id]",
	Short: "Pull project configuration from FastAPI",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		projectID := args[0]
		fmt.Printf("Fetching config for project: %s...\n", projectID)

		token, err := loadToken()
		if err != nil {
			fmt.Printf("Error: Not logged in. Please run 'specter login' first. (%v)\n", err)
			return
		}

		url := "http://localhost:8000/api/configurations/project/" + projectID
		req, _ := http.NewRequest("GET", url, nil)
		req.Header.Set("Authorization", "Bearer "+token)

		client := &http.Client{}
		resp, err := client.Do(req)
		if err != nil {
			fmt.Printf("Error connecting to server: %v\n", err)
			return
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			fmt.Printf("Error: Server returned status %d\n", resp.StatusCode)
			return
		}

		body, err := io.ReadAll(resp.Body)
		if err != nil {
			fmt.Printf("Error reading response: %v\n", err)
			return
		}

		if err := saveConfig(body); err != nil {
			fmt.Printf("Error saving config: %v\n", err)
			return
		}

		fmt.Println("Configuration successfully saved to .specter/config.yaml")
	},
}

func loadToken() (string, error) {
	home, _ := os.UserHomeDir()
	path := filepath.Join(home, ".specter", "auth.json")

	data, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}

	var config AuthConfig // Uses the struct defined in login.go
	if err := json.Unmarshal(data, &config); err != nil {
		return "", err
	}

	return config.AccessToken, nil
}

func saveConfig(content []byte) error {
	dir := ".specter"
	if err := os.MkdirAll(dir, 0755); err != nil {
		return err
	}

	path := filepath.Join(dir, "config.yaml")
	return os.WriteFile(path, content, 0644)
}

func init() {
	rootCmd.AddCommand(pullCmd)
}
