import pandas as pd


class DataProcessor:
    def __init__(self, df_alloc, df_financial) -> None:
        self.df_alloc = df_alloc
        self.df_financial = df_financial
        self.save_path = "processed/"
        self.alloc_filename = "allocations.csv"
        self.financial_filename = "financial.csv"

    def _handle_missing_values_alloc(self) -> None:
        # droping values with missing client
        self.df_alloc = self.df_alloc[~self.df_alloc['Client'].isna()]
        # droping values with missing allocation
        self.df_alloc = self.df_alloc[~self.df_alloc['Target Allocation (%)'].isna()]
        # fill missing values with Unknown
        self.df_alloc.loc[:, ['Target Portfolio', 'Asset Class']] = self.df_alloc[
            ['Target Portfolio', 'Asset Class']
        ].fillna('Unknown')

    def _handle_missing_values_financial(self) -> None:
        # droping values with missing client
        self.df_financial = self.df_financial[~self.df_financial['Client'].isna()]
        # fill missing values with Unknown
        self.df_financial.loc[
            :,
            [
                'Symbol',
                'Name',
                'Sector',
                'Purchase Date',
                'Analyst Rating',
                'Risk Level',
            ],
        ] = self.df_financial[
            [
                'Symbol',
                'Name',
                'Sector',
                'Purchase Date',
                'Analyst Rating',
                'Risk Level',
            ]
        ].fillna(
            'Unknown'
        )
        # dropping missing values
        self.df_financial.dropna(inplace=True)

    def _handle_client_column_financial(self) -> None:
        # get only client ids that are in the allocations table
        self.df_financial = self.df_financial[
            self.df_financial['Client'].isin(self.df_alloc['Client'].unique())
        ]

    def _get_client_id(self):
        self._handle_client_column_financial()

        # get id from client for simplification purposes
        self.df_alloc['Client'] = self.df_alloc['Client'].apply(
            lambda x: x.split('_')[1]
        )
        self.df_financial['Client'] = self.df_financial['Client'].apply(
            lambda x: x.split('_')[1]
        )

    def save_processed_data(self):
        # apply preprocessings
        self._handle_missing_values_alloc()
        self._handle_client_column_financial()
        self._get_client_id()
        # save dataframes
        self.df_alloc.to_csv(self.save_path + self.alloc_filename, index=False)
        self.df_financial.to_csv(self.save_path + self.financial_filename, index=False)
