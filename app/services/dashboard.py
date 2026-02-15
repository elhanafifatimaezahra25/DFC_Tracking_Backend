from sqlmodel import Session, select
from ..models.dfc import DFC
from ..models.user import User
from .. import database
from collections import Counter
from datetime import datetime
from typing import Dict, Any, Optional

def get_basic_stats():
    with Session(database.engine) as session:
        dfcs = session.exec(select(DFC)).all()
        total = len(dfcs)
        open_count = len([d for d in dfcs if d.statut == "ouvert"])
        closed_count = len([d for d in dfcs if d.statut == "ferme"])
        by_project = Counter([d.projet_ref.name for d in dfcs if d.projet_ref])
        return {
            "total": total,
            "open": open_count,
            "closed": closed_count,
            "by_project": dict(by_project)
        }


def get_admin_dashboard(session: Session) -> Dict[str, Any]:
    """
    Get comprehensive admin dashboard with all key metrics.
    This is designed to impress stakeholders with detailed insights.
    """
    dfcs = session.exec(select(DFC)).all()
    users = session.exec(select(User)).all()

    # Total counts
    total_dfc = len(dfcs)
    # Note: ECO would require separate model - placeholder for now
    total_eco = 0

    # DFC by type
    dfc_by_type = dict(Counter([d.type_dfc for d in dfcs if d.type_dfc]))

    # DFC by project (using projet_ref relationship)
    dfc_by_project = dict(
        Counter([d.projet_ref.name for d in dfcs if d.projet_ref])
    )

    # Feasibility rate: count of faisabilite != None / total
    feasible_count = len([d for d in dfcs if d.faisabilite])
    feasibility_rate = round((feasible_count / total_dfc * 100), 2) if total_dfc > 0 else 0

    # Average delay in days
    delays = []
    for d in dfcs:
        if d.date_reception and d.date_reponse:
            delay = (d.date_reponse - d.date_reception).days
            if delay >= 0:  # Only count valid delays
                delays.append(delay)

    average_delay = round(sum(delays) / len(delays), 2) if delays else 0

    # Status distribution
    status_distribution = {
        "ouvert": len([d for d in dfcs if d.statut == "ouvert"]),
        "ferme": len([d for d in dfcs if d.statut == "ferme"])
    }

    # Faisabilité distribution
    faisabilite_dist = dict(Counter([d.faisabilite for d in dfcs if d.faisabilite]))

    return {
        "summary": {
            "total_dfc": total_dfc,
            "total_eco": total_eco,
            "total_users": len(users),
            "open_dfc": status_distribution["ouvert"],
            "closed_dfc": status_distribution["ferme"]
        },
        "dfc_by_type": dfc_by_type,
        "dfc_by_project": dfc_by_project,
        "statistics": {
            "feasibility_rate": f"{feasibility_rate}%",
            "average_delay_days": average_delay,
            "status_distribution": status_distribution,
            "faisabilite_distribution": faisabilite_dist
        },
        "metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "total_metrics": 7
        }
    }
