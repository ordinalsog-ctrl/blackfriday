"""Read-only reporting of evidence readiness. Never fetch or infer missing historic prices."""
import csv, sqlite3
from pathlib import Path

def build_report(db_path, pilot_csv, output_csv):
    with sqlite3.connect(db_path) as conn, open(pilot_csv, encoding="utf-8-sig", newline="") as f:
        conn.row_factory=sqlite3.Row
        pilot=list(csv.DictReader(f))
        results=[]
        for p in pilot:
            pid=p["catalog_id"]
            row=conn.execute("""SELECT COUNT(*) AS n,
                COUNT(DISTINCT substr(observed_at,1,10)) AS days,
                SUM(CASE WHEN review_status='APPROVED' THEN 1 ELSE 0 END) AS approved,
                MIN(observed_at) AS oldest, MAX(observed_at) AS newest
                FROM price_observations WHERE product_id=?""",(pid,)).fetchone()
            n,days,approved=row["n"],row["days"],row["approved"] or 0
            results.append({"product_id":pid,"name":p["product_name_from_pilot"],
                "imported_price_points":n,"observed_days":days,"approved_price_points":approved,
                "earliest":row["oldest"] or "","latest":row["newest"] or "",
                "target_days":21,"missing_observation_days":max(0,21-days),
                "normal_price_ready":"NO" if days<21 or approved<15 else "REVIEW_REQUIRED"})
    with open(output_csv,"w",encoding="utf-8-sig",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=list(results[0]));wr.writeheader();wr.writerows(results)
    return results
