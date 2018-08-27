pipeline {
    agent { docker { image 'python:3.5.1' } }
    stages {
        stage('build') {
            steps {
                timeout(time: 1, unit: 'MINUTES') {
                    retry(2) {
                        sh 'python --version'
                    }
                }
            }
        }
    }
}
