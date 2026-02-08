package cmd

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/joho/godotenv"
	"github.com/spf13/cobra"
)

type MagicLinkRequest struct {
	Email string `json:"email"`
}

type PollResponse struct {
	Status string `json:"status"`
	Token  string `json:"token"`
	ID     string `json:"id"`
}

type AuthConfig struct {
	AccessToken string `json:"access_token"`
	Expiry      int64  `json:"expiry"`
	UserID      string `json:"user_id"`
}

var loginCmd = &cobra.Command{
	Use:   "login",
	Short: "Log in via OTP Code",
	Run: func(cmd *cobra.Command, args []string) {
		mode := os.Getenv("APP_MODE")
		frontendURL := ""
		if mode == "dev" {
			frontendURL = os.Getenv("FRONTEND_URL_DEV")
		} else {
			frontendURL = os.Getenv("FRONTEND_URL_PROD")
		}
		verifyPath := strings.TrimSuffix(frontendURL, "/") + "/verify-otp"

		fmt.Print("Enter your email: ")
		var email string
		fmt.Scanln(&email)
		email = strings.TrimSpace(email)

		fmt.Println("Sending an OTP code to your email...")
		err := triggerMagicLink(email)
		if err != nil {
			fmt.Printf("Error: %v\n", err)
			return
		}

		fmt.Println("\n---------------------------------------------------------")
		fmt.Println("1. Check your email for a 6-digit code.")
		fmt.Println("2. Go to:", verifyPath)
		fmt.Println("3. Enter your email and the code there.")
		fmt.Println("---------------------------------------------------------")
		fmt.Println("Waiting for verification... (Timeout in 5 mins)")

		token, id, err := pollForCompletion(email)
		if err != nil {
			fmt.Printf("Login failed: %v\n", err)
			return
		}

		if err := saveTokenAndID(token, id); err != nil {
			fmt.Printf("Failed to save credentials: %v\n", err)
			return
		}

		fmt.Println("\nSuccessfully logged in! You can now use Specter CLI.")
	},
}

func triggerMagicLink(email string) error {
	mode := os.Getenv("APP_MODE")
	backendURL := ""
	if mode == "dev" {
		backendURL = os.Getenv("BACKEND_URL_DEV")
	} else {
		backendURL = os.Getenv("BACKEND_URL_PROD")
	}
	url := backendURL + "/api/auth/magic-link"
	body, _ := json.Marshal(MagicLinkRequest{Email: email})
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(body))
	if err != nil || resp.StatusCode != http.StatusOK {
		return fmt.Errorf("could not trigger magic link")
	}
	return nil
}

func pollForCompletion(email string) (string, string, error) {
	mode := os.Getenv("APP_MODE")
	backendURL := ""
	if mode == "dev" {
		backendURL = os.Getenv("BACKEND_URL_DEV")
	} else {
		backendURL = os.Getenv("BACKEND_URL_PROD")
	}

	safeEmail := url.QueryEscape(email)
	url := fmt.Sprintf("%s/api/auth/poll?email=%s", backendURL, safeEmail)
	timeout := time.After(5 * time.Minute)
	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-timeout:
			return "", "", fmt.Errorf("login timed out")
		case <-ticker.C:
			resp, err := http.Get(url)
			if err != nil {
				continue
			}
			var result PollResponse
			json.NewDecoder(resp.Body).Decode(&result)
			resp.Body.Close()

			if result.Status == "completed" {
				return result.Token, result.ID, nil
			}
		}
	}
}

func init() {
	err := godotenv.Load("../../.env")
	if err != nil {
		log.Fatal("Error loading .env file")
	}
	rootCmd.AddCommand(loginCmd)
}

func saveTokenAndID(token string, id string) error {
	homeDir, err := os.UserHomeDir()
	if err != nil {
		return err
	}

	configDir := filepath.Join(homeDir, ".specter")
	if err := os.MkdirAll(configDir, 0700); err != nil {
		return err
	}

	authFile := filepath.Join(configDir, "auth.json")

	data := AuthConfig{
		AccessToken: token,
		UserID:      id,
		Expiry:      time.Now().Add(24 * time.Hour).Unix(),
	}

	fileContent, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(authFile, fileContent, 0600)
}
