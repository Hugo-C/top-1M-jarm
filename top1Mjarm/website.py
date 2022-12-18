from dataclasses import dataclass, field


@dataclass
class Website:
    domain: str
    alexa_rank: int
    ip: str = field(default=None)
    jarm: str = field(default=None)

    def to_csv_line(self) -> str:
        return ','.join([
            str(self.alexa_rank),
            self.domain,
            self.ip,
            self.jarm,
        ])
