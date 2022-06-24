import getpass
import logging
import pickle
import sys
import time

import mysql.connector
import pandas as pd
import pymysql
import sqlalchemy
from mysql.connector import errorcode
from openmap.util.log import logger

# logger = logging.getLogger(__name__)

__version__ = "0.1"
__author__ = "Conrard TETSASSI"
__maintainer__ = "Conrard TETSASSI"
__email__ = "giresse.feugmo@gmail.com"
__status__ = "Development"


def countdown(sleeptime):
    for remaining in range(sleeptime, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write(f"{remaining:4d} seconds remaining before next refresh.")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\n")


class RemoteDB:
    """Client to interact with a sql data base"""

    def __init__(self, host, user, port, dbname, password=None):
        self.host = host
        self.user = user
        self.port = port
        self.dbname = dbname
        self.password = password  # getpass.getpass()
        self.conn = None
        self.cursor = None

    @logger.catch
    def _connect(self):
        """Open connection to remote database server."""
        if self.password is None:
            self.password = getpass.getpass(prompt="Enter the database Password: ", stream=None)

        if self.conn is None:
            try:
                logger.info("Opening connection to sql database")
                # self.conn = mysql.connector.connect(host=self.host,
                #                                     user=self.user,
                #                                     port=self.port,
                #                                     password=self.password,
                #                                     database=self.dbname)
                self.conn = pymysql.connect(
                    host=self.host, user=self.user, port=self.port, passwd=self.password, db=self.dbname
                )
                logger.info(f"Connection established to server:    database  [{self.dbname}]")
            # except mysql.connector.Error as error:
            except pymysql.Error as error:
                logger.error(f"Authentication to  MySQL table failed  : {error}")
                raise error
            except TimeoutError:
                logger.error("Timeout.. trying again.")
                # continue
        return self.conn

        # self.conn = self._connect()

    @logger.catch
    def disconnect(self):
        """Close  connection to the database server"""
        try:
            self.cursor.close()
        except Exception as err:
            logger.error(f"{err}")

        try:
            self.conn.close()
            self.conn = None
            logger.warning("database disconnected")
        except Exception as err:
            logger.error(f"{err}")

    @logger.catch
    def checkDbExists(self, DB_NAME=None, dbcon=None):
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        self.cursor = dbcon.cursor()

        if DB_NAME is None:
            DB_NAME = self.dbname

        self.cursor.execute("SHOW DATABASES")

        db_list = [name[0] for name in self.cursor]
        if DB_NAME in db_list:
            self.cursor.close()
            return True

        self.cursor.close()
        return False

    @logger.catch
    def checkTableExists(self, tablename, DB_NAME=None, dbcon=None):
        """
        :param tablename:
        :param dbcon:
        :return:
        """
        if DB_NAME is None:
            DB_NAME = self.dbname

        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        self.cursor = dbcon.cursor()

        self.cursor.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{}'".format(
                tablename.replace("'", "''")
            )
        )
        if self.cursor.fetchone()[0] == 1:
            self.cursor.close()
            logger.info(f"Table [{tablename}] found in the database [{DB_NAME}]")
            return True

        self.cursor.close()
        logger.info(f"Table [{tablename}] not found in the database [{DB_NAME}]")
        return False

    @logger.catch
    def checkColumnExists(self, tablename, colname, dbcon=None):
        """
        :param tablename:
        :param dbcon:
        :return:
        """

        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        self.cursor = dbcon.cursor()

        try:
            sql = f"SHOW columns FROM {tablename}"
            self.cursor.execute(sql)
            colnames = [column[0] for column in self.cursor.fetchall()]
            self.cursor.close()
            if colname in colnames:
                return True
            return False
        except Exception as err:
            logger.error(f" {err}")
            # exit(1)

    @logger.catch
    def create_database(self, DB_NAME=None, dbcon=None):
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        self.cursor = dbcon.cursor()
        if DB_NAME is None:
            DB_NAME = self.dbname

        try:
            self.cursor.execute(f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        except pymysql.Error as err:
            logger.info(f" {err}")
            # print(" {}".format(err))
            # exit(0)

        try:
            self.cursor.execute(f"USE {DB_NAME}")
        except pymysql.Error as err:
            logger.info(f"Database {DB_NAME} does not exists.")
            # print("Database {} does not exists.".format(DB_NAME))
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                # create_database(self.cursor)
                # print("Database {} created successfully.".format(DB_NAME))
                logger.info(f"Database {DB_NAME} created successfully.")
                dbcon.database = DB_NAME
            else:
                logger.error(f" {err}")
                # print(err)
                # exit(1)

    @logger.catch
    def create_table(self, table_name, table_description, DB_NAME=None, dbcon=None, drop=False):
        """
        :param table_name:
        :param table_description:
        :param dbcon:
        :param drop:
        :return:
        """
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        self.cursor = dbcon.cursor()

        if DB_NAME is None:
            DB_NAME = self.dbname

        try:
            logger.info(f"Creating table [{table_name}]: ")
            self.cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                if drop:
                    logger.info(f"Dropping table [{table_name}]: ")
                    self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                else:
                    logger.error(f"Table [{table_name}] already exists.")
            else:
                logger.error(f"{err.msg}")
        else:
            logger.info("Table  created ")

        self.cursor.close()
        # dbcon.close()

    @logger.catch
    def df_to_sql(self, df, tablename, dbcon=None):
        """
        use the sqlalchemy package to upload a Dataframe
        :param df: Dataframe
        :param tablename:
        :param dbcon:
        :return:
        """

        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn

        engine = sqlalchemy.create_engine(
            "mysql+pymysql://{user}:{pw}@{host}/{db}".format(
                host=self.host, db=self.dbname, user=self.user, pw=self.password
            )
        )

        try:
            logger.info(f"Writing  [{tablename}] table  to aws")
            df.to_sql(
                name=tablename,
                con=engine,
                if_exists="append",
                index=False,
                # It means index of DataFrame will save. Set False to ignore
                # the index of DataFrame.
                chunksize=1000,
            )  # Just means chunksize. If DataFrame is big will need this param

        except ValueError as vx:
            logger.error(f"{vx}")

        except Exception as ex:
            logger.error(f"{ex}")

        else:
            logger.info(f"Table {tablename} created successfully")

        finally:
            self.cursor.close()

    @logger.catch
    def insert_Dataframe_to_DB(self, df, tablename, dbcon=None):
        """Insert a entire data frame into sql table"""
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        self.cursor = dbcon.cursor()

        # creating column list for insertion
        cols = "`,`".join([str(i) for i in df.columns.tolist()])

        # Insert DataFrame recrds one by one.
        for i, row in df.iterrows():
            sql = f"INSERT INTO `{tablename}` (`" + cols + "`) VALUES (" + "%s," * (len(row) - 1) + "%s)"
            self.cursor.execute(sql, tuple(row))

            # the connection is not necesserly autocommitted(pymysql,
            # mysql-connection)  , so we must commit to save our changes
        try:
            dbcon.commit()
        except BaseException:
            pass
        finally:
            self.cursor.close()

    @logger.catch
    def df_to_sqltable(self, df, tablename, DB_NAME=None, dbcon=None, drop=False):
        """
        :param df: DataFrame to upload
        :param tablename: name of the table
        :param DB_NAME:
        :param dbcon:
        :param drop: drop the table if exists
        :return:
        """

        colms = ["`" + i + "`" for i in df.columns.tolist()]
        types = [str(df[col].dtypes) for col in df.columns.tolist()]
        # if isinstance(row[prop], (np.ndarray, np.generic)):
        for i, typ in enumerate(types):
            if typ == "object":
                types[i] = "varchar(255)"
            elif typ == "float64" or "float32":
                types[i] = "FLOAT"  # 'DECIMAL(12, 6)'
            elif typ == "int64" or "int32":
                types[i] = "INT"

        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        self.cursor = dbcon.cursor()

        if DB_NAME is None:
            DB_NAME = self.dbname

        description = [" ".join([i, j]) for i, j in zip(colms, types)]

        description = ",".join([str(i) for i in description])
        sql = f"CREATE TABLE {tablename}  (" + description + ")"

        try:
            logger.info(f"Creating table [{tablename}]: ")
            self.cursor.execute(sql)

            # creating column list for insertion
            cols = "`,`".join([str(i) for i in df.columns.tolist()])

            # Insert DataFrame recrds one by one.
            for i, row in df.iterrows():
                sql = f"INSERT INTO `{tablename}` (`" + cols + "`) VALUES (" + "%s," * (len(row) - 1) + "%s)"
                self.cursor.execute(sql, tuple(row))
            try:
                dbcon.commit()
            except BaseException:
                pass

            logger.info(f"Table [{tablename}] has been  created  successfully")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                if drop:
                    logger.info(f"Dropping table [{tablename}]: ")
                    self.cursor.execute(f"DROP TABLE IF EXISTS {tablename}")
                    self.cursor.execute(f" CREATE TABLE {tablename}  (" + description + ")}")

                    # creating column list for insertion
                    cols = "`,`".join([str(i) for i in df.columns.tolist()])

                    # Insert DataFrame recrds one by one.
                    for i, row in df.iterrows():
                        sql = f"INSERT INTO `{tablename}` (`" + cols + "`) VALUES (" + "%s," * (len(row) - 1) + "%s)"
                        self.cursor.execute(sql, tuple(row))
                    try:
                        dbcon.commit()
                    except BaseException:
                        pass

                    logger.info(f"Table [{tablename}] has been  created successfully")
                else:
                    logger.error(f"Table [{tablename}] already exists.")
            else:
                logger.error(f" {err.msg}")

        self.cursor.close()
        # dbcon.close()

    @logger.catch
    def read_table_to_df(self, tablename, dbcon=None):
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn

        try:
            pandas_df = pd.read_sql(f"SELECT * FROM  {tablename}", dbcon)
        except ValueError as vx:
            logger.error(f"{vx}")

        except Exception as ex:
            logger.error(f"{ex}")

        else:
            logger.info(f"Table {tablename} loaded successfully to  Dataframe")

        finally:
            self.cursor.close()
        return pandas_df

    @logger.catch
    def load_table_to_pandas(self, tablename, dbcon=None):
        """
        :param tablename: name of the table
        :param dbcon: connection to the database
        :return: pandas dataframe
        """
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn

        pandas_df = pd.read_sql(f"select * from {tablename} ", dbcon)

        for col in pandas_df.columns:
            try:
                pandas_df[col] = pandas_df.apply(lambda x: pickle.loads(x[col]), axis=1)
            except BaseException:
                continue

        for col in pandas_df.columns:
            try:
                pandas_df[col] = pandas_df.apply(lambda x: x[col].decode(), axis=1)
            except BaseException:
                continue

        return pandas_df

    @logger.catch
    def get_columns_name(self, table_name, dbcon=None):
        """

        :param table_name:
        :param dbcon:
        :return: Column Names
        """
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        try:
            self.cursor = dbcon.cursor()
            sql_select_query = f"select * from  {table_name}"
            self.cursor.execute(sql_select_query)
            field_names = [i[0] for i in self.cursor.description]
        except Exception as ex:
            logger.error(f"{ex}")
        finally:
            self.cursor.close()
        return field_names

    # def get_value(self,tablename, colame, id_col,rowname, dbcon=None):
    #     """
    #
    #     :param tablename:
    #     :param colame:
    #     :param rowname:
    #     :param dbcon:
    #     :return: the value  value of colame/rowname,
    #     """
    #     if dbcon is None:
    #         self.conn = self._connect()
    #         dbcon = self.conn
    #     try:
    #         self.cursor = dbcon.cursor()
    #         sql = f"SELECT {colame} FROM {tablename} WHERE  {id_col}={rowname}"
    #         self.cursor.execute(sql)
    #         myresult = self.cursor.fetchall()
    #     except Exception as ex:
    #         logger.error(f"{ex}")
    #     finally:
    #         self.cursor.close()
    #     return myresult

    # def get_structrure(self, tablename, struc_id, dbcon=None):
    #     """
    #     :param tablename:
    #     :param struc_id: list of id to fecth
    #     :param dbcon:
    #     :return: return a list of Ase Atoms class
    #     """
    #
    #     if dbcon is None:
    #         self.conn = self._connect()
    #         dbcon = self.conn
    #
    #     field_names = self.get_columns_name(tablename, dbcon)
    #
    #     self.cursor = dbcon.cursor()
    #     atms = []
    #     sql_select_query = "select * from  {} where id = %s".format(tablename)
    #     for struc in struc_id:
    #         self.cursor.execute(sql_select_query, (struc_id,))
    #         record = self.cursor.fetchall()
    #         numbers = pickle.loads(record[0][field_names.index('numbers')])
    #         positions = pickle.loads(record[0][field_names.index('positions')])
    #         cell = pickle.loads(record[0][field_names.index('cell')])
    #         #pbc = pickle.loads(record[0][field_names.index('pbc')])
    #
    #         atm = Atoms(numbers=numbers, positions=positions, cell=cell)
    #         atms.append(atm)
    #     self.cursor.close()
    #     return atms
    @logger.catch
    def get_value(self, tablename, colname, id_col, rowname, dbcon=None):
        """
        :param tablename: name of the table
        :param colname: column to check
        :param id_col: name of the column with structure id
        :param rowname: id of the structure == row
        :param dbcon: connection to db
        :return: return value of column [colname] at row [rowname]
        """
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn

        self.cursor = dbcon.cursor()
        try:
            sql_select_query = f"select {colname} from  {tablename} where {id_col} ='{rowname}' "
            self.cursor.execute(sql_select_query)
            record = self.cursor.fetchone()
            return record[0]
        except Exception as ex:
            logger.error(f"{ex}")
            # raise Exception(f"{ex}")
        finally:
            self.cursor.close()

    @logger.catch
    def add_column(self, tablename, colname, coltype, dbcon=None):
        """
        add column in a table
        :param tablename:
        :param colname:
        :param coltype: type off the colunm to add
        :param dbcon:
        :return:
        """

        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        try:
            self.cursor = dbcon.cursor()
            sql = f"ALTER TABLE  {tablename} ADD {colname} {coltype}"
            self.cursor.execute(sql)
            logging.info(f"Table [{tablename}] altered with column [{colname}]")
        except Exception as ex:
            logger.error(f"{ex}")
        finally:
            self.cursor.close()

    @logger.catch
    def drop_column(self, tablename, colname, dbcon=None):
        """
        drop a column in a table
        :param tablename:
        :param colname:
        :param dbcon:
        :return:
        """

        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        try:
            self.cursor = dbcon.cursor()
            sql = f"ALTER TABLE  {tablename} DROP COLUMN  {colname}"
            self.cursor.execute(sql)
            logging.info(f" column [{colname}] in table [{tablename}]")
        except Exception as ex:
            logger.error(f"{ex}")
        finally:
            self.cursor.close()

    @logger.catch
    def insert_value(self, tablename, colname, val, id_col, struc_id, dbcon=None):
        """
        :param tablename:
        :param colname:
        :param val:
        :param id_col:
        :param struc_id:
        :param dbcon:
        :return:
        """

        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        try:
            self.cursor = dbcon.cursor()
            sql = f"UPDATE   {tablename} SET  {colname}= {val} WHERE {id_col}='{struc_id}'"
            self.cursor.execute(sql)
        except Exception as ex:
            logger.error(f"{ex}")
        finally:
            dbcon.commit()
            self.cursor.close()

    @logger.catch
    def monitoring(self, jobs, tablename, colname, id_col, sleeptime=120, dbcon=None):
        """
        :param jobs: list of dictionary with job information
        :return:
        """
        # if dbcon is None:
        #     self.disconnect()
        #     self.conn = self._connect()
        #     dbcon = self.conn
        # self.cursor = dbcon.cursor()

        status_list = [None for job in jobs]
        while not all(status is not None for status in status_list):
            self.disconnect()
            status_list = [self.get_value(tablename, colname, id_col, job) for job in jobs]
            for job, status in zip(jobs, status_list):
                if status is not None:
                    logger.info(f"{job}: COMPLETED")
                else:
                    logger.info(f"{job}: PENDING")
            #
            if all(status is not None for status in status_list):
                logger.info("All Jobs COMPLETED")
                continue
            else:
                countdown(sleeptime)

        return status_list
