# ----------------------------------------------------------------------------
# Copyright (c) 2012-2018, American Gut Project development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import jinja2
import seaborn as sns
import matplotlib.pyplot as plt
from io import StringIO
import pandas as pd


class Reporter:
    def __init__(alpha, beta, taxa, mf, samples):
        self.host_type = 'HOST_TYPE'
        self.host_subject_id = 'HOST_SUBJECT_ID'
        self.sample_type = 'SAMPLE_TYPE'

        self._alpha = alpha
        self._beta = beta
        self._taxa = taxa

        self._mf = mf
        self._samples = set(samples)

    def plot_alpha(self, subset):
        """

        Parameters
        ---------
        subset: list of str
            A list of samples to highlight in an alpha diversity plot.
        """

        if len(subset) > 1:
        # if more than 1 sample for the participant
        # distribution rotated 90deg. and line plot of alpha diversity over time

            fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)

            # create a line plot
            tiny_mf = self._mf.loc[subset].copy()
            tiny_mf['α'] = self._alpha[subset]
            tiny_mf['Time'] = pd.to_datetime(tiny_mf['collection_timestamp'],
                                             errors='coerce')
            main_plot = sns.pointplot(x="Time",
                                      y="α",
                                      data=tiny_mf,
                                      ax=ax2)

            for tick in ax2.get_xticklabels():
                tick.set_rotation(90)

        else:
        # Note: remember the subaxis plot
        # use distribution plot and add a vertical line indicating the sample
            fig, ax1 = plt.subplots(1)

        # distribution: all of AG for a given sample type
        ag_distplot = sns.distplot(alpha, vertical=(len(subset)>1),
                                   hist=False, ax=ax1)

        imgdata = StringIO()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)  # rewind the data

        svg_data = imgdata.getvalue()  # this is svg data

        # return a plot (SVG)
        return svg_data

    def plot_beta(self, subset):
        """

        Parameters
        ---------
        subset: list of str
            A list of samples to highlight in an alpha diversity plot.
        """
        # makes a scatter plot based on pc1, pc2 and colored by body site
        # highlights the subset of samples

        # return a plot (SVG)
        return None

    def summarize_taxa(self, subset):
        """

        Parameters
        ---------
        subset: list of str
            A list of samples to highlight in an alpha diversity plot.
        """
        # reuses whatever was on the latex thing

        # return an HTML-formatted Pandas dataframe
        return None

    def iter_sample_types(self, subject_sub):
        """Iterate over the sample types in a subject's dataframe

        Parameters
        ----------
        subset : pd.DataFrame
            A metadata subset for a subject's (implying subject identifier
            and subject type) samples. This is usually as generated by the
            iter_subjects method.

        Yields
        ------
        str
            At every iteration yields the unique sample types for this subject.
        pd.DataFrame
            The subset of the metadata corresponding to each subject's
            sample types.
        """
        for sample_type, st_subset in subject_sub.groupby([self.sample_type]):
            yield sample_type, st_subset

    def iter_subjects(self):
        """Iterate over the subject ids and subject types in the metadata

        Yields
        ------
        str
            The subject's identifier, as described by the column in
            ``self.host_subject_id``.
        str
            The subject's host type, as described by the column in
            ``self.host_type``.
        pd.DataFrame
            The subset of the metadata corresponding to each subject's samples.
        """
        # expects to yield the subject ids and subject types
        sub = self.mf.loc[self._samples].copy()

        for vals, df in sub.groupby([self.host_subject_id, self.host_type]):
            host_subject_id, host_type = vals
            yield host_subject_id, host_type, df


class ReporterView:
    template_for_plots = 'plot-grid.html'

    def __init__(self, reporter):
        path = pkg_resources.resource_filename('q2_american_gut', 'assets',
                                               'report')

        loader = jinja2.FileSystemLoader(searchpath=path)
        environment = jinja2.Environment(loader=loader)
        self.plot_grid = environment.get_template(self.template_for_plots)

        self.reporter = reporter

    def render_plots(self, sample_type_subset):

        s = sample_type_subset.index.tolist()

        taxa = self.reporter.summarize_taxa(s)
        beta = self.reporter.plot_beta(s)
        alpha = self.reporter.plot_alpha(s)

        # create a template of some sort with all these things
        return self.plot_grid.render(taxa=taxa, beta=beta, alpha=alpha)

    def site_translator(self, site_name):
        # translate between category names and emojis
        # eg oral -> *tongue emoji*

        return '?'
