from urllib import request
import cx_Oracle
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
from plotly.graph_objs import *
from flask import Flask, jsonify
from flask import render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('ejemplo.html')


@app.route('/_cargar_charts')
def cargar_charts():
    # archivos de texto con los resultados de las query
    outfile = open('Resultados_Query_MEMLIBRE.txt', 'w')  # archivo de salida con los resultados de las query
    outfile2 = open('Resultados_Query_UsuariosConectados.txt', 'w')  # archivo de salida con los resultados de las query
    outfile3 = open('Resultados_Query_TABLESPACE.txt', 'w')  # archivo de salida con los resultados de las query
    outfile4 = open('Resultados_Query_TEMPORAL.txt', 'w')  # archivo de salida con los resultados de las query

    con = cx_Oracle.connect('system/manager@10.217.0.23:1535/UVMDVL')  # conexion a la BD

    # query para memoria libre
    select = "select POOL, Round(bytes/1024/1024,0) Free_Memory_In_MB "
    desde = "from V$sgastat "
    where = "where Name Like '%free memory%' "

    # ejecucion query mem libre
    cur = con.cursor()
    cur.execute(select + desde + where)

    for result in cur:
        # print result
        # print "Pool: "+list(result)[0] +" Free Memory: "+str(list(result)[1])
        outfile.write(str(result) + "\n")

    cur.close()
    outfile.close()

    # Query Usuarios Conectados
    select = "select substr(a.spid,1,9) pid,substr(b.sid,1,5) sid,substr(b.serial#,1,5) ser#,substr(b.machine,1,6) box,substr(b.username,1,10) username,b.server,substr(b.osuser,1,8) os_user,substr(b.program,1,30) program "
    desde = "from v$session b, v$process a "
    where = "where b.paddr = a.addr and type='USER' "
    order = "order by spid"

    # ej query Usuarios Conectados
    cur2 = con.cursor()
    cur2.execute(select + desde + where + order)

    TotalUsCone = 0
    for result in cur2:
        # print list(result)[4]
        # print result  muestra por pantalla las tuplas obtenidas de la bd
        TotalUsCone += 1
        outfile2.write(str(result) + "\n")

    # creacion grafico barras
    data = Data([
        Bar(
            x="Usuarios Conectados",
            y=TotalUsCone
        )
    ])

    layout = go.Layout(
        title='Cantidad Usuarios Conectados',
        font=Font(
            family='Raleway, sans-serif'

        ),
        showlegend=True,
        xaxis=XAxis(
            tickangle=-45
        ),
        bargap=0.05
    )
    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(data, filename='Usuarios Conectados UVM', auto_open=False)

    cur2.close()
    outfile2.close()

    # query Tablespaces
    select = "select df.tablespace_name Tablespace,totalusedspace Used_MB,(df.totalspace - tu.totalusedspace) Free_MB,df.totalspace Total_MB, Round((df.totalspace-tu.totalusedspace)/df.totalspace) Pct_Free "
    # tabla df
    aux = "(select tablespace_name,Round(sum(bytes) / 1048576) TotalSpace from dba_data_files group by tablespace_name) df,"
    # Table TU
    aux2 = "(select round(sum(bytes)/(1024*1024)) totalusedspace, tablespace_name from dba_segments group by tablespace_name) tu where df.tablespace_name = tu.tablespace_name "

    # Ejecucion Tablespace
    cur3 = con.cursor()
    cur3.execute(select + "from " + aux + aux2)

    for result in cur3:
        if list(result)[0] == "UNDOTBS1":
            # print result
            listaPC1 = list(result)
            labels = ['Usado', 'Libre']
            values = [listaPC1[1], listaPC1[2]]
            trace = go.Pie(labels=labels, values=values)
            py.iplot([trace], filename='Uso Memoria UNDOTBS1')
            outfile3.write(str(result) + "\n")

        if list(result)[0] == "SYSTEM":
            # print result
            listaPC2 = list(result)
            labels2 = ['Usado', 'Libre']
            values2 = [listaPC2[1], listaPC2[2]]
            trace = go.Pie(labels=labels2, values=values2)
            py.iplot([trace], filename='Uso Memoria SYSTEM')
            outfile3.write(str(result) + "\n")

    cur3.close()
    outfile3.close()

    select = "SELECT A.tablespace_name tablespace, D.mb_total,SUM(A.used_blocks * D.block_size)/1024/1024 mb_used,(D.mb_total - SUM(A.used_blocks * D.block_size)/1024/1024) mb_free "
    desde = "FROM v$sort_segment A, "
    aux = "(SELECT B.name,C.block_size,(SUM(C.bytes)/1024/1024) mb_total  FROM v$tablespace B, v$tempfile C Where B.ts#= C.ts# Group by B.name,C.block_size) D "
    where = "WHERE A.tablespace_name = D.name "
    group = "GROUP by A.tablespace_name, D.mb_total"

    cur4 = con.cursor()
    cur4.execute(select + desde + aux + where + group)
    for result in cur4:
        outfile4.write(str(result) + "\n")
        listaPC3 = list(result)
        labels3 = ['Usado', 'Libre']
        values3 = [listaPC3[2], listaPC3[3]]
        trace = go.Pie(labels=labels3, values=values3)
        py.iplot([trace], filename='Uso Memoria TEMP')

    cur4.close()
    con.close()
    outfile4.close()
    return jsonify("hola")


@app.route('/_saludar')
def saludar():
    return jsonify("hola")

if __name__ == '__main__':
    app.run(debug=True)



