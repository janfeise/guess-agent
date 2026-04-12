const dbName = "guess_agent";
const database = db.getSiblingDB(dbName);

database.createCollection("games");
database.games.createIndex({ game_id: 1 }, { unique: true });
database.games.createIndex({ status: 1 });
