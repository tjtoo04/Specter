package cmd

import (
	"context"
	"fmt"
	"io"
	"os"

	"github.com/docker/docker/api/types/image"
	"github.com/docker/docker/client"
	"github.com/spf13/cobra"
)

func init() {
	rootCmd.AddCommand(runCmd)
}

var runCmd = &cobra.Command{
	Use:   "run",
	Short: "Start the Specter agent",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Initializing Specter Agent...")

		// TODO: Change docker image
		imageName := "your-docker-repo/specter-agent:latest"
		err := pullAgentImage(imageName)
		if err != nil {
			fmt.Printf("Error pulling agent image: %v\n", err)
			return
		}

		fmt.Println("Agent image is ready. Starting container...")
	},
}

func pullAgentImage(imageName string) error {
	ctx := context.Background()

	// Initialize the Docker client
	cli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		return fmt.Errorf("unable to connect to Docker: %w", err)
	}

	fmt.Printf("Pulling image: %s\n", imageName)

	out, err := cli.ImagePull(ctx, imageName, image.PullOptions{})
	if err != nil {
		return err
	}
	defer out.Close()

	_, err = io.Copy(os.Stdout, out)
	if err != nil {
		return fmt.Errorf("error reading pull progress: %w", err)
	}

	return nil
}
