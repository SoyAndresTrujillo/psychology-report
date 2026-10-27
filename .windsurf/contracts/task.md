<Motivation>
The project is based a system to help to carry the registers of the patients, doctor's office, psycologist and appointments.
</Motivation>

<Models>
- Fields for each entity
  - accounts
    - name
    - last_name
    - age
    - gender
    - phone
    - email
    - role: {patient, psycologist}

  - appointments
    - account_id
    - psycologist_id
    - date
    - time
    - status
    
  - doctors
    - account_id
    - doctors_office_id
    - speciality
    
  - doctors_office
    - name
    - address
    - phone
    - email
    - psycologist_id
</Models>

<APIs>
The system should be have the next API's:
- /api/accounts/create (this should be a POST request)
- /api/appointments/create (this should be a POST request)
- /api/doctors/create (this should be a POST request)
- /api/doctors_office/create (this should be a POST request)
- /api/appointment-report (this should be a GET request)
</APIs> 

<Views>
  First Form create account and should be connect with the API /api/accounts/create:
    - name
    - last_name
    - age
    - gender (this should be a dropdown)
    - phone (this should be a phone number)
    - email
    - role: {patient, psycologist} (this should be a dropdown)
    - doctor's office (if the role's dropdown is psycologist then this should be a dropdown with the name of the doctor's office, if the form sent the values it should be save the doctor's office_id)
    - speciality (if the role's dropdown is psycologist then this should be a dropdown with the speciality of the psycologist, if the form sent the values it should be save the speciality)

  Second Form create appointment and should be connect with the API /api/appointments/create:
    - account_id (this should be a dropdown with the patient's name and last name combined, if the form sent the values it should be save the account_id)
    - psycologist_id (this should be a dropdown with the psycologist's name and last name combined, if the form sent the values it should be save the psycologist_id)
    - date
    - time
    - status

  Third Form create doctor and should be connect with the API /api/doctors/create:
    - account_id (this should be a dropdown with the psycologist's name and last name combined, if the form sent the values it should be save the account_id)
    - doctors_office_id (this should be a dropdown with the doctor's office's name, if the form sent the values it should be save the doctors_office_id)
    - speciality (this should be a dropdown with the speciality of the psycologist, if the form sent the values it should be save the speciality)

  Fourth Form create doctor's office and should be connect with the API /api/doctors_office/create:
    - name
    - address
    - phone
    - email
    - psycologist_id (this should be a dropdown with the psycologist's name and last name combined, if the form sent the values it should be save the psycologist_id)

  Fifth a table appointment report with the API /api/appointment-report:
    - headers
     - Patient (this should a name + last_name)
     - Psycologist (this should a name + last_name)
     - Doctor's office
     - Date
     - Time
     - Status
</Views>

<DockerCompose>
version: '3.8'

services:
  postgres:
    image: postgres:15
    env_file: .env
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    ports:
      - '5432:5432'
    volumes:
      - ./postgres_data:/var/lib/postgresql/data
    networks:
      - logistics-back
networks:
  logistics-back:
    driver: bridge
# COMMANDS: docker-compose -f docker-compose.dev.yml up -d, docker-compose -f docker-compose.dev.yml down
</DockerCompose>

<Stack>
- Python
- Django
- PostgreSQL
- Docker
</Stack>

<Restrictions>
- The project should have the content knowledge into the django tutorials, what are:
  - tutorial 1: https://docs.djangoproject.com/en/5.2/intro/tutorial01/
  - tutorial 2: https://docs.djangoproject.com/en/5.2/intro/tutorial02/
  - tutorial 3: https://docs.djangoproject.com/en/5.2/intro/tutorial03/
  - tutorial 4: https://docs.djangoproject.com/en/5.2/intro/tutorial04/
</Restrictions>

<Content>
  - Creación de entorno virtual
  - Creación de Apps
  - Creación de Vistas
  - Creación de Modelos
  - Migraciones
  - Tablas Relacionadas (No puede haber tablas solitarias, debe haber mínimo una relación)
  - Rutas dinámicas para pasar parámetros a las vistas
  - Templates
  - Manejo de Error 404
  - Shortcuts
  - Formularios
  - Manejo de datos enviados desde formularios
</Content>