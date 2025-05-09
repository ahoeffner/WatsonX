import psycopg


class SQL :
	def getDepartures(self,origin:str,destination:str,daterange:list) -> list:
		self.connect()

		query = "select * from departures " 	+ \
				  "where origin = '{origin}' " 		+ \
				  "and destination = '{destination}' " + \
				  "and departure between '{fr}' and '{to}' order by departure"

		query = query.format(origin=origin, destination=destination, fr=daterange[0], to=daterange[1])

		#print("SQL query:", query)
		result = self.executeQuery(query)

		self.disconnect()

		if not result:
			return "No flights found"

		tab = "The following list of flights were found:\n"

		for row in result:
			tab += "Flight: "+row[1] + ", " \
					 "From: "+row[2] + ", " \
					 "Departing: "+row[4].strftime("%Y-%m-%d %H:%M")  + ", " \
					 "Available seats: "+str(row[5]) + "\n"

		return tab


	def bookSeats(self, flight:str, seats:int) -> str :
		self.connect()

		sql = "update departures " 	+ \
				  "set available_seats = available_seats - {seats} " + \
				"where flight = '{flight}'"

		sql = sql.format(flight=flight, seats=seats)

		result:bool = self.executeUpdate(sql)
		self.disconnect()

		if (result) : return f"{seats} seat(s) has successful been booked on flight "+flight
		else : return "No seats available on flight "+flight


	def connect(self) -> None :
		db_params = {
			"dbname": "ai",
			"user": "ai",
			"password": "ai",
			"host": "localhost",
			"port": 5432
		}
		self.conn = psycopg.connect(**db_params)


	def disconnect(self) -> None :
		if hasattr(self, 'conn'):
			self.conn.close()
			del self.conn


	def executeQuery(self, query:str) -> list :
		if not hasattr(self, 'conn'):
			self.connect()

		with self.conn.cursor() as cursor:
			cursor.execute(query)
			result = cursor.fetchall()

		return result


	def executeUpdate(self, stmt:str) -> bool :
		result = False

		if not hasattr(self, 'conn'):
			self.connect()

		with self.conn.cursor() as cursor:
			cursor.execute(stmt)
			if cursor.rowcount > 0:
				result = True
				self.conn.commit()

		return result



if __name__ == "__main__":
	sql = SQL()
	sql.test("CPH","AMS",["2025-04-07","2025-04-10"])