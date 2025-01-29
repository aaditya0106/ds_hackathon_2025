card_css = """
    <style>
        .card {
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 10px;
            box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.1);
            background-color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.1s ease-in-out, box-shadow 0.1s ease-in-out;
        }
        .card:hover {
            transform: scale(1.02);
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2);
        }
        .card img {
            width: 80px;
            height: auto;
            border-radius: 5px;
        }
        .card-content {
            flex: 3;
            text-align: left;
        }
        .card-image {
            flex: 1;
            text-align: right;
        }
        .details-button {
            margin-top: 10px;
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 5px;
            font-size: 14px;
            cursor: pointer;
        }
        .details-button:hover {
            background-color: #0056b3;
        }
    </style>
"""

wide_dialog_css = """
    <style>
        div[data-testid="stDialog"] div[role="dialog"]:has(.big-dialog) {
            width: 50vw;
        }
    </style>
"""

def apt_css(apt):
    return (
        f"""
        <div class="card">
            <div class="card-content">
                <strong>{apt['buildingName']}</strong><br>
                {apt['address']}<br>
                <strong>Price:</strong> ${int(apt['price'])}
            </div>
            <div class="card-image">
                <img src="{apt['imgSrc']}" alt="Apartment Image">
            </div>
        </div>
        """
    )