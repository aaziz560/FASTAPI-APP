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

        stage('EXECUTE POSTGRES') {
            steps {
                script {
                    // Exécutez la commande Docker inspect pour obtenir l'adresse IP du conteneur PostgreSQL
                    def postgresIP = sh(script: 'docker inspect -f \'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}\' postgres-container', returnStdout: true).trim()
        
                    // Exposez l'adresse IP de PostgreSQL en tant que variable d'environnement
                    sh "export POSTGRES_IP=$postgresIP"
        
                    // Lancez le conteneur PostgreSQL
                    sh 'docker-compose up -d'
                }
            }
        }

        stage('Checkout UNITTESTS') {
            steps {
                script {
                    // Utilisez la variable d'environnement POSTGRES_IP lors de l'exécution des tests
                    sh "export POSTGRES_IP=$POSTGRES_IP && python3 -m unittest test.py"
                }
            }
        }


       
        stage('Deploy with Docker Compose') {
            steps {
                script {
                    sh 'docker-compose up -d'
                }
            }
        }

    }

}
