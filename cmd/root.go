package cmd

import "github.com/spf13/cobra"

var rootCmd = &cobra.Command{ // Lowercase is fine as long as other files are 'package cmd'
	Use:   "specter",
	Short: "Specter CLI",
}

func Execute() error {
	return rootCmd.Execute()
}
