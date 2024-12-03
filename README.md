![EU Logo](https://www.xamk.fi/app/uploads/sites/2/2024/04/FI_Co-fundedbytheEU_RGB_POS-e1724236553174-768x168.png)
1. Ensure you have docker installed
2. Clone the repository
3. Run sudo docker build -t somenameyouwanttouse .
4. Run sudo docker run -p 8089:8089 --name anothernamebutcanbethesmae -d --restart unless-stopped somenameyouwanttouse
   If you want to change the port changed it to .py script, dockerfile and to this run command.
