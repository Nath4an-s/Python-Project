import os
import webbrowser
from Units import *
from Building import *

def generate_html_report(players):
    html_content = """
    <html>
    <head>
        <title>Game Units, Buildings, and Resources Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .collapsible {
                background-color: #f1f1f1;
                color: black;
                cursor: pointer;
                padding: 10px;
                width: 100%;
                border: none;
                text-align: left;
                outline: none;
                font-size: 15px;
            }
            .active, .collapsible:hover {
                background-color: #ccc;
            }
            .content {
                padding: 0 18px;
                display: none;
                overflow: hidden;
                background-color: #f9f9f9;
            }
            .info {
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <h1>Game Units, Buildings, and Resources Report</h1>
    """

    # Define unit categories
    unit_categories = {
        'Villager': [],
        'Swordsman': [],
        'Horseman': [],
        'Archer': []
    }

    # Define building categories
    building_categories = {
        'Town Center': [],
        'House': [],
        'Camp': [],
        'Farm': [],
        'Barracks': [],
        'Stable': [],
        'Archery Range': [],
        'Keep': []
    }

    # Sort units and buildings into categories
    for player in players:
        # Reset unit and building categories for each player
        unit_categories = {key: [] for key in unit_categories.keys()}
        building_categories = {key: [] for key in building_categories.keys()}

        for unit in player.units:
            if isinstance(unit, Villager):
                unit_categories['Villager'].append(unit)
            elif isinstance(unit, Swordsman):
                unit_categories['Swordsman'].append(unit)
            elif isinstance(unit, Horseman):
                unit_categories['Horseman'].append(unit)
            elif isinstance(unit, Archer):
                unit_categories['Archer'].append(unit)

        for building in player.buildings:
            if isinstance(building, TownCenter):
                building_categories['Town Center'].append(building)
            elif isinstance(building, House):
                building_categories['House'].append(building)
            elif isinstance(building, Camp):
                building_categories['Camp'].append(building)
            elif isinstance(building, Farm):
                building_categories['Farm'].append(building)
            elif isinstance(building, Barracks):
                building_categories['Barracks'].append(building)
            elif isinstance(building, Stable):
                building_categories['Stable'].append(building)
            elif isinstance(building, ArcheryRange):
                building_categories['Archery Range'].append(building)
            elif isinstance(building, Keep):
                building_categories['Keep'].append(building)

        # Add player info and unit categories
        html_content += f"<h2>{player.name}</h2>"  # Single title for the player
        max_population_build = sum([building.population_increase for building in player.buildings])

        # Population and resources on the same line
        html_content += f"""
            <p class='info'>Population: {player.population}/{max_population_build} | 
            Wood: {player.owned_resources['Wood']} | 
            Food: {player.owned_resources['Food']} | 
            Gold: {player.owned_resources['Gold']}</p>
        """

        # Units collapsible section
        html_content += "<button class='collapsible'>Show Units</button>"
        html_content += "<div class='content'>"

        # Add unit categories under player units
        for category, unit_list in unit_categories.items():
            unit_count = len(unit_list)  # Count the number of units
            html_content += f"<button class='collapsible'>{category} ({unit_count})</button>"
            html_content += "<div class='content'>"
            if unit_list:
                for unit in unit_list:
                    html_content += f"<h3>{unit.name} (HP: {unit.hp})</h3>"
                    html_content += f"<p>Position: ({unit.position[0]:.2f}, {unit.position[1]:.2f})</p>"
                    html_content += f"<p>Current Task: {unit.task}</p>"
            else:
                html_content += "<p>No units yet</p>"
            html_content += "</div>"

        html_content += "</div>"

        # Buildings collapsible section
        html_content += "<button class='collapsible'>Show Buildings</button>"
        html_content += "<div class='content'>"

        # Add building categories under player buildings
        for category, building_list in building_categories.items():
            building_count = len(building_list)  # Count the number of buildings
            html_content += f"<button class='collapsible'>{category} ({building_count})</button>"
            html_content += "<div class='content'>"
            if building_list:
                for building in building_list:
                    html_content += f"<h3>{building.name} (HP: {building.hp})</h3>"
                    html_content += f"<p>Position: {building.position}</p>"
            else:
                html_content += "<p>No buildings yet</p>"
            html_content += "</div>"

        html_content += "</div>"

    html_content += """
        <script>
            var coll = document.getElementsByClassName("collapsible");
            for (let i = 0; i < coll.length; i++) {
                coll[i].addEventListener("click", function() {
                    this.classList.toggle("active");
                    var content = this.nextElementSibling;
                    if (content.style.display === "block") {
                        content.style.display = "none";
                    } else {
                        content.style.display = "block";
                    }
                });
            }
        </script>
    </body>
    </html>
    """

    report_file = "game_units_report.html"
    with open(report_file, "w") as file:
        file.write(html_content)

    print("HTML report generated: game_units_report.html")

    # Open the HTML report in the default web browser
    webbrowser.open(f'file://{os.path.realpath(report_file)}')
