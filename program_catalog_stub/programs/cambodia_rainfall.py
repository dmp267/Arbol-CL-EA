from program_catalog_stub.program_utils.loader import ArbolLoader


_PROGRAM_PARAMETERS = ['dataset', 'locations', 'start', 'end', 'strike', 'limit', 'opt_type', 'tick']

def _generate_payouts(data, start, end, opt_type, strike, tick, limit):
    ''' Uses the provided contract parameters to calculate a payout and index

        Parameters: data (Pandas Series), weather data averaged over locations
                    start (date str), start date of coverage period
                    end (date str), end date of coverage period
                    opt_type (str), type of option contract, either PUT or CALL
                    strike (number), strike value for the contract
                    tick (number), tick value given in the sro
                    limit (number), limit value for the payout
        Returns: number, generated payout
    '''
    index_value = data.loc[start:end].sum()
    opt_type = opt_type.lower()
    direction = 1 if opt_type == 'call' else -1
    payout = (index_value - strike) * tick * direction
    if payout < 0:
        payout = 0
    if payout > limit:
        payout = limit
    return float(round(payout, 2))


class CambodiaRainfall:
    ''' Program class for Cambodia rainfall contracts. Validates requests,
        retrieves weather data from IPFS, computes an average over the given
        locations, and evaluates whether a payout should be awarded
    '''
    @classmethod
    def validate_request(cls, params):
        ''' Uses program-specific parameter requirements to validate a given
            request

            Parameters: params (dict), parameters to be checked against the
            requirements
            Returns: bool, whether the request format is valid
                     str, error message in the event that the request is not valid
        '''
        result = True
        result_msg = ''
        for param in _PROGRAM_PARAMETERS:
            if not param in params:
                result_msg += f'missing {param} parameter\n'
                result = False
        return result, result_msg

    @classmethod
    def serve_evaluation(cls, params):
        ''' Loads the relevant geospatial historical weather data and computes
            a payout and an index

            Parameters: params (dict), dictionary of required contract parameters
            Returns: number, the determined payout (0 if not awarded)
        '''
        loader = ArbolLoader(locations=params['locations'],
                            dataset_name=params['dataset'],
                            imperial_units=params.get('imperial_units', False)
                            )
        avg_history = loader.load()
        payout = _generate_payouts(data=avg_history,
                                    start=params['start'],
                                    end=params['end'],
                                    opt_type=params['opt_type'],
                                    strike=params['strike'],
                                    tick=params['tick'],
                                    limit=params['limit']
                                    )
        return payout
