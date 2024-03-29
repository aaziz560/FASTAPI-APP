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
                    sh 'docker run --name test-postgres \
                      -e POSTGRES_USER=aziz \
                      -e POSTGRES_PASSWORD=aziz \
                      -p 5435:5432 \
                      -v local_pgdata:/var/lib/postgresql/data \
                      -d postgres:latest'

                    
                }
            }
        }


        stage('Checkout UNITTESTS') {
            steps {
                script {
 
                    def postgresIP = sh(script: 'docker inspect -f "{{.NetworkSettings.IPAddress}}" test-postgres', returnStdout: true).trim()
                    
                    echo "Postgres IP: ${postgresIP}"
                    
                    env.POSTGRES_IP = postgresIP
                    
                    sh 'python3 -m venv venv'
                    sh 'chmod +x install_dependecies.sh'
                    sh 'sh install_dependecies.sh'
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
