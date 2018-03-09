import json


def make_ranking_from_pk(file, year):
    with open(file, "r") as f:
        teams = json.load(f)

    ranking = [{"model": "march_madness.teamrank",
                "pk": None,
                "fields": {
                    "year": year,
                    "team": item["pk"],
                    "seed": item["pk"]
                    }} for item in teams]

    new_filename = "team_ranking_"+str(year)+".json"
    with open(new_filename, "w") as f:
        json.dump(ranking, f, indent=2)

    return new_filename


if __name__ == '__main__':
    FILENAME = "teams.json"
    make_ranking_from_pk(FILENAME, 2018)
