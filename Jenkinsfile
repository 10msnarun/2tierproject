pipeline {
    agent any
    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Build Docker Image') { steps { sh 'docker build -t my-python-app:latest .' } }
        stage('Deploy with Compose') {
            steps {
                sh 'docker-compose down || true'
                sh 'docker-compose up -d --build'
            }
        }
        stage('Integration Test') {
            steps {
                sh 'sleep 10'
                sh 'curl -f http://localhost/health'
            }
        }
    }
}
