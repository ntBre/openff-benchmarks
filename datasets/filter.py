import click
from openff.qcsubmit.results import OptimizationResultCollection
from openff.qcsubmit.results.filters import (
    ConnectivityFilter,
    RecordStatusEnum,
    RecordStatusFilter,
    SinglepointRecordFilter,
)
from openff.qcsubmit.utils import _CachedPortalClient, portal_client_manager
from openff.toolkit.utils.exceptions import (
    ChargeCalculationError,
    ConformerGenerationError,
)
from openff.toolkit.utils.toolkits import OpenEyeToolkitWrapper


class ChargeCheckFilter(SinglepointRecordFilter):
    def _filter_function(self, result, record, molecule) -> bool:
        try:
            OpenEyeToolkitWrapper().assign_partial_charges(
                molecule, partial_charge_method="am1bccelf10"
            )
        except (ChargeCalculationError, ConformerGenerationError):
            return False
        else:
            return True


@click.command()
@click.option("--input-file", "-i")
@click.option("--output-file", "-o")
@click.option("--pretty-print", "-p", is_flag=True)
def main(input_file, output_file, pretty_print):
    ds = OptimizationResultCollection.parse_file(input_file)
    client = _CachedPortalClient(
        "https://api.qcarchive.molssi.org:443/", cache_dir="."
    )
    with portal_client_manager(lambda _: client):
        ds = ds.filter(
            RecordStatusFilter(status=RecordStatusEnum.complete),
            ConnectivityFilter(tolerance=1.2),
            ChargeCheckFilter(),
        )
    with open(output_file, "w") as out:
        if pretty_print:
            out.write(ds.json(indent=2))
        else:
            out.write(ds.json())


if __name__ == "__main__":
    main()
