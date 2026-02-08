package cmd

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/joho/godotenv"
	"github.com/spf13/cobra"
)

var pullCmd = &cobra.Command{
	Use:   "pull [project_id]",
	Short: "Pull project configuration from FastAPI",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		mode := os.Getenv("APP_MODE")
		backendURL := ""
		if mode == "dev" {
			backendURL = os.Getenv("BACKEND_URL_DEV")
		} else {
			backendURL = os.Getenv("BACKEND_URL_PROD")
		}

		token, id, err := loadToken()
		if err != nil {
			fmt.Printf("Error: Not logged in. Please run 'specter login' first. (%v)\n", err)
			return
		}

		requestBody, _ := json.Marshal(map[string]string{
			"user_id": id,
		})

		configPath := strings.TrimSuffix(backendURL, "/") + "/api/configs/project/"
		projectID := args[0]
		fmt.Printf("Fetching config for project: %s...\n", projectID)

		url := configPath + projectID
		req, _ := http.NewRequest("POST", url, bytes.NewBuffer(requestBody))
		req.Header.Set("Authorization", "Bearer "+token)
		req.Header.Set("Content-Type", "application/json")

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

		fmt.Print(string(body))
		if err := saveConfig(body); err != nil {
			fmt.Printf("Error saving config: %v\n", err)
			return
		}

		fmt.Println("Configuration successfully saved to .specter/config.yaml")
	},
}

func loadToken() (string, string, error) {
	home, _ := os.UserHomeDir()
	path := filepath.Join(home, ".specter", "auth.json")

	data, err := os.ReadFile(path)
	if err != nil {
		return "", "", err
	}

	var config AuthConfig
	if err := json.Unmarshal(data, &config); err != nil {
		return "", "", err
	}

	return config.AccessToken, config.UserID, nil
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
	err := godotenv.Load("../../.env")
	if err != nil {
		log.Fatal("Error loading .env file")
	}
	rootCmd.AddCommand(pullCmd)
}
