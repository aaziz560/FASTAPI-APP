pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                script {
                    git branch: 'main', changelog: false, poll: false, url: 'https://github.com/aaziz560/FASTAPI-APP.git'
                }
            }
        }

       
        stage('Deploy with Docker Compose') {
            steps {
                script {
                    bat 'docker-compose up -d'
                }
            }
        }

    }

}
