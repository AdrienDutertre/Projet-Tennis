Pré-processing : 
================

Ce répertoire rassemble toutes les opérations de pre-processing des données : 
- concaténation de toutes les années disponibles 
- normalisation de certains champs (scores, noms des joueurs, etc.)
- randomisation de la base (autant de victoires de joueur a que b)
- obtention des classements des joueurs (crawling)
- obtention d'infos sur les joueurs (dob, taille, poids, etc.) (crawling)
- obtention des matchs manquants (maters cup) (crawling) (TO-DO)

Le but de ce répertoire est donc de partir des données brutes, de les nettoyer et de les enrichir. 
Ces données "pré-traitées" sont ensuite écrites sous la forme de trois csv : 
- players.csv : contient les infos et classements de chaque joueur
- rankings.csv : contient les classements uniquement de chaque joueur
- matchs.csv : contient les infos sur les matchs et leurs stats

Enfin un dernier script permet d'avoir une version SQL de ces données (TO-DO).
Le schéma SQL retenu est alors le suivant : 
- table matchs 
- table tournaments 
- table players
- table rankings

Enchaînement des scripts 
------------------------
Pour obtenir la version SQL en partant des données brutes il faut respecter l'enchaînement suivant

1. extractRanking
2. mergeRanking
3. extractPlayersInfo
4. getMatchsWithRankings
5. createSqlTables (TO-DO)

Descriptions des scripts
-------------------------

Script | Description
------------ | -------------
extractRanking | Obtention des classements des joueurs par blocs via crawling
mergeRanking | Fusion des différents blocs de classements en un seul
extractMissingTournaments | Rajout du tournoi World Tour
extractPlayersInfo | Obtention des infos des joueurs et jointure avec leurs classements
getMatchsWithRankings | Obtention des matchs avec jointure vers les classements pour chaque match
createSqlTables (TO-DO) | Création du schéma SQL représentant les données pré-traitées

 
