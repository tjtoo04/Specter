package main

import (
	"log"

	"github.com/tjtoo04/specter/cmd"
)

func main() {
	if err := cmd.Execute(); err != nil {
		log.Fatalf("Failed to execute command: %v", err)
	}
}
