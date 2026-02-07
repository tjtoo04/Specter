package cmd


import (
	"fmt"
	"io"
	"net/http"
	"os"

	"github.com/spf13/cobra"
)
// Default API URL (change this to your actual default)
var apiHost string

// pullCmd represents the pull command
var pullCmd = &cobra.Command{
	Use:   "pull",
	Short: "Fetch projects from the API",
	Long:  `Sends a GET request to the /api/projects endpoint to retrieve a list of projects.`,
	Run: func(cmd *cobra.Command, args []string) {
		// 1. Construct the URL
		url := fmt.Sprintf("%s/api/projects", apiHost)
		fmt.Printf("Fetching from: %s\n", url)

		// 2. Make the GET request
		resp, err := http.Get(url)
		if err != nil {
			fmt.Printf("Error making request: %v\n", err)
			os.Exit(1)
		}
		defer resp.Body.Close()

		// 3. Check for non-200 status codes
		if resp.StatusCode != http.StatusOK {
			fmt.Printf("Error: Received status code %d\n", resp.StatusCode)
			os.Exit(1)
		}

		// 4. Read and print the response body
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			fmt.Printf("Error reading response: %v\n", err)
			os.Exit(1)
		}

		// Print the raw JSON response
		fmt.Println(string(body))
	},
}

func init() {
	// This registers the command with the root command so "specter pull" works
	rootCmd.AddCommand(pullCmd)

	// Add a flag to specify the host (defaults to localhost:8080)
	pullCmd.Flags().StringVar(&apiHost, "host", "https://specterai.duckdns.org", "Base URL for the API")
}