!function () {

  // memorize some data
  const els = {
    results: document.querySelector( '.results a' ),
    errors:  document.querySelector( '.errors a' ),
  };
  els.results.dataset.href = els.results.getAttribute( 'href' );
  els.errors.dataset.href  = els.errors.getAttribute( 'href' );
  let analysisData = null;

  // trigger updates
  updateStats();
  setInterval(updateStats, 30 * 1000);

  // other listeners
  document.querySelector('#eval button').addEventListener( 'click', updateEval );
  document.querySelector('#audit button').addEventListener( 'click', updateAudit );
  document.querySelector('#missingMappings button').addEventListener( 'click', updateMissingMappings );
  document.querySelector('#analysis button').addEventListener( 'click', updateCandidateAnalysis );
  document.querySelector('#analysisOverview').addEventListener( 'click', showAnalysisDetails );


  /**
   * fetch the current sets of statistics and display them
   */
  async function updateStats() {
    const stats = await (await fetch( './getStats', { method: 'POST'} )).json();

    // fill in static routes
    fillElements( stats );

    // progress bar
    document.querySelector( '.progress .tabresult' ).style.width = (100 * stats.tables.result / stats.tables.total) + '%';
    document.querySelector( '.progress .taberror' ).style.width = (100 * stats.tables.error / stats.tables.total) + '%';
    const progressTitle = `Results: ${(100 * stats.tables.result / stats.tables.total).toFixed(2)}% | Errors: ${(100 * stats.tables.error / stats.tables.total).toFixed(2)}%`;
    ['.progress', '.progress .tabresult', '.progress .taberror']
      .forEach( (sel) => document.querySelector( sel ).setAttribute( 'title', progressTitle ) );

    // update file availability
    for( const link of [ 'results', 'errors' ] ) {
      if( stats.files[ link ] ) {
        els[ link ].classList.remove( 'disabled');
        els[ link ].setAttribute( 'href', els[ link ].dataset.href );
      } else {
        els[ link ].classList.remove( 'disabled');
        els[ link ].removeAttribute( 'href' );
      }
    }

    // checkmark for finished
    if( stats.tables.unfinished < 1 ) {
      document.querySelector( '.finishedFlag' ).classList.add( 'finished' );
    } else {
      document.querySelector( '.finishedFlag' ).classList.remove( 'finished' );
    }

    // enable/disable evaluation section
    document.querySelector('#eval').style.display = stats.hasEvaluation ? 'block' : 'none';
    document.querySelector('#analysis').style.display = stats.hasEvaluation ? 'block' : 'none';

  }


  /**
   * update the evaluation section on demand
   */
  async function updateEval() {
    const eval = await (await fetch( './getEvaluation', { method: 'POST'} )).json();
    fillElements( eval );
  }


  /**
   * update data-path elements from the given data object
   */
  function fillElements( data ) {
    const nodes = Array.from( document.querySelectorAll('[data-path]') );
    for( const node of nodes ) {
      const path = node.dataset.path.split('.');
      let value = data, el;
      while( el = path.shift() ) {
        if( el in value ) {
          value = value[el];
        } else {
          break;
        }
      }
      if( typeof value != 'object' ) {
        node.innerHTML = value != undefined ? value : '-';
      }
    }
  }

    /**
   * update the audit section on demand
   */
  async function updateAudit() {
    const eval = await (await fetch( './getAudit', { method: 'POST'} )).json();
    fillAuditElements( eval['res'] );

  }

  /**
   * update specific cells of audit table given data
   */
  function fillAuditElements( data ) {

    for( const item of data ) {

        // pick specific parts of item
        let step = item['step']
        let task = item['task']

        // determines and selects the target cell
        // determination step heavily relies on the id formula i.e., c_cea = creation[0] and lower case of task (CEA)
        let target_el_id = "#" +step[0] + "_" + task.toLowerCase()
        const target_td = document.querySelector(target_el_id);

        methods = ""
        for (const method of item['methods']){
            // concatenates methods given name, #solved_cnt and a newline
            methods = methods +  method[0] + ", " + method[1] + "</br>"
        }

        // Updates the HTML of the target cell
        target_td.innerHTML = methods

      }
    }


  /**
   * update the list of missing mappings
   */
  async function updateMissingMappings(){

    // fetch data
    const allData = await (await fetch( './getMissingMappings', { method: 'POST'} )).json();

    // assemble output
    const out = [];
    for( const [type, data] of Object.entries(allData) ) {

      // create table for missing all
      const missAll = [ `<table>
        <thead><tr><th>No Mappings</th></tr></thead>
        <tbody><tr><th>Name</th></tr>` ];
      for( const entry of data.missingAll ) {
        missAll.push(`<tr><td>${entry.table_name}</td></th>`);
      }
      missAll.push( '</tbody></table>' );

      // create table for missing parts
      const missPart = [ `<table>
        <thead><tr><th colspan="3">Missing Some Mappings</th></tr></thead>
        <tbody><tr><th>Name</th><th>Missing</th><th>Total</th></tr>` ];
      for( const entry of data.missingPart ) {
        missPart.push(`
          <tr>
            <td>${entry.table_name}</td>
            <td>${entry.missing}</td>
            <td>${entry.total}</td>
          </tr>
        `)
      }
      missPart.push('</tbody></table>')

      // add section for that
      out.push( `
      <fieldset>
        <legend>${type.toUpperCase()}</legend>
        ${missAll.join('')}
        ${missPart.join('')}
      </fieldset> 
      `);

    }

    // insert to the DOM
    document.querySelector( '#missingMappings > div' ).innerHTML = out.join('\n');
  }

  

  /**
   * update the analysis of candidates
   */
  async function updateCandidateAnalysis(){

    // empty detail window
    document.querySelector('#analysisDetail .header').innerHTML = '';
    document.querySelector('#analysisDetail .tab').innerHTML = '';

    // fetch data
    analysisData = await (await fetch( './getAnalysis', { method: 'POST'} )).json();

    for( const type of [ 'cea', 'cpa', 'cta'] ) {

      // get drawn version
      const vis = drawAnalysis( type, analysisData[type].agg );

      // add to the corresponding container
      document.querySelector( `#analysis${type.toUpperCase()}` ).innerHTML = vis;

    }

  }


  /**
   * upon click on a given row of the analysis table, show the detailed view
   */
  function showAnalysisDetails( ev ){
    
    // only trigger on clicks to the headers
    if( ev.target.tagName != 'TH' ) {
      return;
    }

    // grab the respective settings
    const key = ev.target.dataset.key,
          type = ev.target.dataset.type;

    // gather the data
    const data = analysisData[ type ].tables.reduce( (all, tab) => {
      all[ tab.table ] = tab.stats[ key ];
      return all;
    }, {} );

    // draw into details box
    const content = drawAnalysis( '', data );
    document.querySelector('#analysisDetail .tab').innerHTML = content;

    // display the header
    document.querySelector('#analysisDetail > div.header' ).innerHTML = `${type.toUpperCase()} - ${key}`;

  }


  /**
   * visualize one set of analysis results
   *
   * @param {string} type
   * @param {object} data
   * @param {Array} order
   */
  function drawAnalysis( type, data, order ) {

    // default order is alphabetical
    if( !order ) {
      order = Object.keys(data).sort( (a,b) => a.localeCompare(b) );
    }

    const out = [ '<table>' ];
    for( const key of order ) {
      const values = data[key],
            corr = (100 * values.correct / values.total).toFixed(2),
            incorr = (100 * values.incorrect / values.total).toFixed(2);
      out.push(`
        <tr title="total: ${values.total} | correct: ${values.correct} | incorrect: ${values.incorrect} | missing: ${values.missing}">
          <th data-key="${key}" data-type="${type}">${key}</th>
          <td><div class="progress tabtotal"><div class="tabresult" style="width: ${corr}%"></div><div class="taberror" style="width: ${incorr}%"></div></div></td>
        </tr>
      `)
    }
    out.push('</table>');

    return out.join('');

  }


}();