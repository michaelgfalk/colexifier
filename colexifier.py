import pandas as pd
import sqlite3

class Colexifier():
    """Connects to an SQLite database and provides methods for finding colexifications"""
    
    def __init__(self, path_to_database = 'clics.sqlite'):
        self.conn = sqlite3.connect(path_to_database)
        self.c = self.conn.cursor()
        
        # Add indexes to database if they don't exist, to speed up performance
        self.c.execute("""
        CREATE INDEX IF NOT EXISTS concepticon_id_index
        ON ParameterTable (Concepticon_ID, Concepticon_Gloss COLLATE NOCASE)
        """)
        self.c.execute("""
        CREATE INDEX IF NOT EXISTS all_concepts_index
        ON ParameterTable (Concepticon_ID, ID, Dataset_ID)
        """)
        self.c.execute("""
        CREATE INDEX IF NOT EXISTS clics_form_index
        ON FormTable (Language_ID, clics_form, Dataset_ID)
        """)
        
        # Commit all changes to indexes
        self.conn.commit()
        
        return None
    
    def get_concepticon_id(self, concept):
        """For a given word, return a Concepticon ID number
        
        Args:
            concept: a string, the concept you are interested in
            
        Returns:
            concepticon_id: a string, the id number of the concept in Concepticon
        """
        
        _concept_id = """
        SELECT p.Concepticon_ID
        FROM ParameterTable as p
        WHERE p.Concepticon_Gloss = ?
        COLLATE NOCASE
        LIMIT 1
        """
        
        concept = (str(concept),) # Search parameter must be a tuple
        
        self.c.execute(_concept_id, concept)
        concepticon_id = self.c.fetchall()
        
        if len(concepticon_id) == 0:
            print(f'No ID number found for the concept "{concept}". Perhaps try another?')
            return None
        
        concepticon_id = concepticon_id[0][0] # Squeeze the value out of the listed tuple
        
        return concepticon_id
    
    def find_concepts(self, concepticon_id):
        """Locates all the concepts that correspond to the given Concepticon ID in the database.
        
        Args:
            concepticon_id: the id number of the concept in concepticon
        
        Returns:
            concept_list: a list of tuples, giving the ID and Dataset ID for the concept
                in the ConceptTable
        """
        
        _all_concepts = """ 
        SELECT p.ID, p.Dataset_ID
        FROM ParameterTable AS p
        WHERE Concepticon_ID = ?
        """ 
        
        concepticon_id = (str(concepticon_id),) # Search parameter must be a tuple
        
        self.c.execute(_all_concepts, concepticon_id)
        concept_list = self.c.fetchall()
        
        return(concept_list)
    
    def find_forms(self, concept_list):
        """Finds all the word forms that correspond to a given Concepticon concept in the Database.
        
        Args:
            concept_list: A list of tuples giving the locations of a given concept
                in the CLICS2 Database, as returned by Colexifier.find_concepts().
        
        Returns:
            form_list: A list of tuples, giving the Language ID, CLICS form and Dataset ID
                of each word form.
        """
        
        _all_words = """
        SELECT f.Language_ID, f.clics_form, f.Dataset_ID
        FROM FormTable AS f
        WHERE f.Parameter_ID = ? AND f.Dataset_ID = ?;
        """
        
        form_list = []
        for tup in concept_list:
            self.c.execute(_all_words, tup)
            form_list += self.c.fetchall()
        
        return form_list
    
    def find_colexes(self, form_list):
        """Given a list of word forms corresponding to a given concept, find all
        other words with the same form, i.e. find colexifications for that concept.
        
        Args:
            form_list: A list of tuples giving the Language ID, CLICS form and Dataset ID
                of each word form, as returned by Colexifier.find_forms()
                
        Returns:
            colex_df: A pandas DataFrame with information about all the colexifications.
        """
        
        _colex = """
        SELECT f.Language_ID, l.Name, f.Form, f.clics_form, p.Concepticon_ID, p.Concepticon_Gloss
        FROM FormTable AS f
        LEFT JOIN ParameterTable AS p
            ON f.Parameter_ID = p.ID AND f.Dataset_ID = p.Dataset_ID
        LEFT JOIN LanguageTable AS l
            ON f.Language_ID = l.ID AND f.Dataset_ID = l.Dataset_ID
        WHERE f.Language_ID = ? AND f.clics_form = ? AND f.Dataset_ID = ?
        """
        
        _columns = ['lang_id','lang_name','word','clics_form','concepticon_id','concepticon_gloss']
        
        colex_list = []
        for tup in form_list:
            self.c.execute(_colex, tup)
            fetched = self.c.fetchall()
            if len(fetched) > 1:
                colex_list += fetched
            
        colex_df = pd.DataFrame(colex_list, columns = _columns)
        
        return colex_df
    
    def search_with_concept(self, concept, out = None):
        """Find all colexification for a given concept.
        
        Args:
            concept: a string, the name of the concept you wish to search
            out (optional): a string, a filename to save the results"""
        
        concepticon_id = self.get_concepticon_id(concept)
        
        # Break out if no Concepticon ID found for the given concept
        if not concepticon_id:
            return None
        
        concept_list = self.find_concepts(concepticon_id)
        form_list = self.find_forms(concept_list)
        colex_df = self.find_colexes(form_list)
        
        if out:
            colex_df.to_csv(out)
            print(f'Colexification data for {concept} saved at {out}')
        
        return(colex_df)
    
    def search_with_id(self, concepticon_id, out = None):
        """Find all colexifications for a given Concepticon ID number."""
        
        concept_list = self.find_concepts(concepticon_id)
        form_list = self.find_forms(concept_list)
        colex_df = self.find_colexes(form_list)
        
        if out:
            colex_df.to_csv(out)
            print(f'Colexification data for {concepticon_id} saved at {out}')
        
        return(colex_df)