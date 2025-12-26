import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Language = 'fr' | 'en';

interface I18nState {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const translations: Record<Language, Record<string, string>> = {
  fr: {
    // Header
    'site.name': 'DISPARUS.ORG',
    'site.tagline': 'Retrouver les disparus',
    'nav.home': 'Accueil',
    'nav.search': 'Rechercher',
    'nav.report': 'Signaler',
    'nav.about': 'À propos',
    'search.placeholder': 'Rechercher par nom, ID, ville...',
    'btn.report': 'Signaler une disparition',
    
    // Hero stats
    'hero.title': 'Ensemble, retrouvons les disparus',
    'hero.subtitle': 'Plateforme citoyenne de signalement et de recherche de personnes disparues en Afrique',
    'stats.missing': 'Personnes signalées',
    'stats.found': 'Retrouvées',
    'stats.countries': 'Pays couverts',
    'stats.contributions': 'Signalements citoyens',
    
    // Filters
    'filter.all': 'Tous',
    'filter.children': 'Enfants',
    'filter.adults': 'Adultes',
    'filter.seniors': 'Personnes âgées',
    'filter.status': 'Statut',
    'filter.status.all': 'Tous les statuts',
    'filter.status.missing': 'Disparu',
    'filter.status.found': 'Retrouvé',
    'filter.status.deceased': 'Décédé',
    'filter.country': 'Pays',
    'filter.country.all': 'Tous les pays',
    'filter.hasPhoto': 'Avec photo',
    'filter.dateFrom': 'Depuis',
    
    // Missing person card
    'card.age': 'ans',
    'card.missing_since': 'Disparu depuis',
    'card.last_seen': 'Dernier lieu',
    'card.view_details': 'Voir détails',
    'card.urgent': 'URGENT',
    
    // Report form
    'form.title': 'Signaler une disparition',
    'form.step': 'Étape',
    'form.step.identity': 'Identité',
    'form.step.location': 'Lieu et circonstances',
    'form.step.description': 'Description',
    'form.step.contact': 'Contact',
    'form.personType': 'Type de personne',
    'form.personType.child': 'Enfant (0-17 ans)',
    'form.personType.adult': 'Adulte (18-59 ans)',
    'form.personType.senior': 'Personne âgée (60+ ans)',
    'form.firstName': 'Prénom',
    'form.lastName': 'Nom de famille',
    'form.age': 'Âge exact',
    'form.sex': 'Sexe',
    'form.sex.male': 'Masculin',
    'form.sex.female': 'Féminin',
    'form.sex.unspecified': 'Non spécifié',
    'form.country': 'Pays de disparition',
    'form.city': 'Ville/Commune',
    'form.physicalDescription': 'Description physique',
    'form.physicalDescription.placeholder': 'Taille, corpulence, signes distinctifs...',
    'form.photo': 'Photo (JPG/PNG, max 5Mo)',
    'form.disappearanceDate': 'Date et heure de disparition',
    'form.circumstances': 'Circonstances exactes',
    'form.circumstances.placeholder': 'Décrivez les circonstances de la disparition...',
    'form.location': 'Lieu de dernière observation',
    'form.location.help': 'Cliquez sur la carte ou utilisez la géolocalisation',
    'form.clothing': 'Vêtements portés',
    'form.belongings': 'Objets emportés',
    'form.contacts': 'Personnes de référence',
    'form.contact.name': 'Nom complet',
    'form.contact.phone': 'Téléphone',
    'form.contact.email': 'Email (optionnel)',
    'form.contact.relation': 'Relation',
    'form.addContact': 'Ajouter un contact',
    'form.removeContact': 'Supprimer',
    'form.consent': "J'autorise la publication de ces informations et confirme leur véracité",
    'form.gdpr': 'Données traitées conformément au RGPD',
    'form.submit': 'Soumettre le signalement',
    'form.next': 'Suivant',
    'form.previous': 'Retour',
    'form.required': 'Champ obligatoire',
    
    // Detail page
    'detail.id': 'ID',
    'detail.status': 'Statut',
    'detail.status.missing': 'Disparu',
    'detail.status.found': 'Retrouvé',
    'detail.status.deceased': 'Décédé',
    'detail.age': 'Âge',
    'detail.sex': 'Sexe',
    'detail.lastSeen': 'Dernière observation',
    'detail.clothing': 'Vêtements',
    'detail.belongings': 'Objets',
    'detail.circumstances': 'Circonstances',
    'detail.physicalDescription': 'Description physique',
    'detail.contacts': 'Contacts de référence',
    'detail.timeline': 'Historique des signalements',
    'detail.contribute': 'Ajouter une information',
    'detail.share': 'Partager',
    'detail.download.pdf': 'Télécharger PDF',
    'detail.download.image': 'Image réseaux sociaux',
    'detail.flag': 'Signaler un problème',
    
    // Contribution form
    'contribution.title': 'Contribuer une information',
    'contribution.type': 'Type de contribution',
    'contribution.type.sighting': 'J\'ai vu cette personne',
    'contribution.type.info': 'Information importante',
    'contribution.type.police_report': 'Signalé à la police',
    'contribution.type.found': 'Personne retrouvée',
    'contribution.type.other': 'Autre',
    'contribution.location': 'Lieu (optionnel)',
    'contribution.date': 'Date/Heure d\'observation',
    'contribution.details': 'Détails précis',
    'contribution.proof': 'Preuve photo/vidéo (optionnel)',
    'contribution.foundState': 'État de la personne',
    'contribution.foundState.safe': 'Saine et sauve',
    'contribution.foundState.injured': 'Blessée',
    'contribution.foundState.deceased': 'Décédée',
    'contribution.returnCircumstances': 'Circonstances du retour',
    'contribution.contact': 'Vos coordonnées (optionnel)',
    'contribution.submit': 'Envoyer',
    
    // Moderation
    'moderation.title': 'Signaler un contenu',
    'moderation.reason': 'Raison du signalement',
    'moderation.reason.false_info': 'Information fausse',
    'moderation.reason.duplicate': 'Doublon',
    'moderation.reason.inappropriate': 'Contenu inapproprié',
    'moderation.reason.spam': 'Spam',
    'moderation.reason.other': 'Autre',
    'moderation.details': 'Précisez (optionnel)',
    'moderation.contact': 'Votre contact (optionnel)',
    'moderation.submit': 'Signaler',
    'moderation.success': 'Merci pour votre signalement',
    
    // Timeline
    'timeline.sighting': 'Observation signalée',
    'timeline.info': 'Information reçue',
    'timeline.police_report': 'Signalé à la police',
    'timeline.found': 'Personne retrouvée',
    'timeline.other': 'Autre contribution',
    'timeline.created': 'Signalement créé',
    
    // How to help
    'help.title': 'Comment aider ?',
    'help.report.title': 'Signaler une disparition',
    'help.report.desc': 'Remplissez un formulaire complet pour signaler une personne disparue',
    'help.contribute.title': 'Apporter une information',
    'help.contribute.desc': 'Ajoutez des informations sur un cas existant si vous avez vu la personne',
    'help.share.title': 'Partager sur les réseaux',
    'help.share.desc': 'Diffusez les avis de recherche pour augmenter les chances de retrouver les disparus',
    
    // Footer
    'footer.about': 'À propos',
    'footer.privacy': 'Confidentialité',
    'footer.terms': 'Conditions d\'utilisation',
    'footer.contact': 'Contact',
    'footer.countries': 'Pays couverts',
    
    // PWA / Offline
    'offline.title': 'Mode hors ligne',
    'offline.message': 'Certaines fonctionnalités sont limitées sans connexion',
    'offline.cached': 'Contenu mis en cache disponible',
    
    // General
    'loading': 'Chargement...',
    'error': 'Une erreur est survenue',
    'retry': 'Réessayer',
    'save': 'Enregistrer',
    'cancel': 'Annuler',
    'close': 'Fermer',
    'yes': 'Oui',
    'no': 'Non',
    'or': 'ou',
    'viewMore': 'Voir plus',
    'noResults': 'Aucun résultat',
    'success': 'Succès',
  },
  en: {
    // Header
    'site.name': 'DISPARUS.ORG',
    'site.tagline': 'Finding the missing',
    'nav.home': 'Home',
    'nav.search': 'Search',
    'nav.report': 'Report',
    'nav.about': 'About',
    'search.placeholder': 'Search by name, ID, city...',
    'btn.report': 'Report a disappearance',
    
    // Hero stats
    'hero.title': 'Together, let\'s find the missing',
    'hero.subtitle': 'Citizen platform for reporting and searching for missing persons in Africa',
    'stats.missing': 'Reported missing',
    'stats.found': 'Found',
    'stats.countries': 'Countries covered',
    'stats.contributions': 'Citizen reports',
    
    // Filters
    'filter.all': 'All',
    'filter.children': 'Children',
    'filter.adults': 'Adults',
    'filter.seniors': 'Seniors',
    'filter.status': 'Status',
    'filter.status.all': 'All statuses',
    'filter.status.missing': 'Missing',
    'filter.status.found': 'Found',
    'filter.status.deceased': 'Deceased',
    'filter.country': 'Country',
    'filter.country.all': 'All countries',
    'filter.hasPhoto': 'With photo',
    'filter.dateFrom': 'Since',
    
    // Missing person card
    'card.age': 'years old',
    'card.missing_since': 'Missing since',
    'card.last_seen': 'Last seen',
    'card.view_details': 'View details',
    'card.urgent': 'URGENT',
    
    // Report form
    'form.title': 'Report a disappearance',
    'form.step': 'Step',
    'form.step.identity': 'Identity',
    'form.step.location': 'Location & circumstances',
    'form.step.description': 'Description',
    'form.step.contact': 'Contact',
    'form.personType': 'Person type',
    'form.personType.child': 'Child (0-17 years)',
    'form.personType.adult': 'Adult (18-59 years)',
    'form.personType.senior': 'Senior (60+ years)',
    'form.firstName': 'First name',
    'form.lastName': 'Last name',
    'form.age': 'Exact age',
    'form.sex': 'Sex',
    'form.sex.male': 'Male',
    'form.sex.female': 'Female',
    'form.sex.unspecified': 'Unspecified',
    'form.country': 'Country of disappearance',
    'form.city': 'City/Town',
    'form.physicalDescription': 'Physical description',
    'form.physicalDescription.placeholder': 'Height, build, distinctive features...',
    'form.photo': 'Photo (JPG/PNG, max 5MB)',
    'form.disappearanceDate': 'Date and time of disappearance',
    'form.circumstances': 'Exact circumstances',
    'form.circumstances.placeholder': 'Describe the circumstances of the disappearance...',
    'form.location': 'Last known location',
    'form.location.help': 'Click on the map or use geolocation',
    'form.clothing': 'Clothing worn',
    'form.belongings': 'Items carried',
    'form.contacts': 'Reference contacts',
    'form.contact.name': 'Full name',
    'form.contact.phone': 'Phone',
    'form.contact.email': 'Email (optional)',
    'form.contact.relation': 'Relationship',
    'form.addContact': 'Add contact',
    'form.removeContact': 'Remove',
    'form.consent': 'I authorize the publication of this information and confirm its accuracy',
    'form.gdpr': 'Data processed in accordance with GDPR',
    'form.submit': 'Submit report',
    'form.next': 'Next',
    'form.previous': 'Back',
    'form.required': 'Required field',
    
    // Detail page
    'detail.id': 'ID',
    'detail.status': 'Status',
    'detail.status.missing': 'Missing',
    'detail.status.found': 'Found',
    'detail.status.deceased': 'Deceased',
    'detail.age': 'Age',
    'detail.sex': 'Sex',
    'detail.lastSeen': 'Last seen',
    'detail.clothing': 'Clothing',
    'detail.belongings': 'Belongings',
    'detail.circumstances': 'Circumstances',
    'detail.physicalDescription': 'Physical description',
    'detail.contacts': 'Reference contacts',
    'detail.timeline': 'Report history',
    'detail.contribute': 'Add information',
    'detail.share': 'Share',
    'detail.download.pdf': 'Download PDF',
    'detail.download.image': 'Social media image',
    'detail.flag': 'Report an issue',
    
    // Contribution form
    'contribution.title': 'Contribute information',
    'contribution.type': 'Contribution type',
    'contribution.type.sighting': 'I saw this person',
    'contribution.type.info': 'Important information',
    'contribution.type.police_report': 'Reported to police',
    'contribution.type.found': 'Person found',
    'contribution.type.other': 'Other',
    'contribution.location': 'Location (optional)',
    'contribution.date': 'Observation date/time',
    'contribution.details': 'Precise details',
    'contribution.proof': 'Photo/video proof (optional)',
    'contribution.foundState': 'Person\'s condition',
    'contribution.foundState.safe': 'Safe and sound',
    'contribution.foundState.injured': 'Injured',
    'contribution.foundState.deceased': 'Deceased',
    'contribution.returnCircumstances': 'Return circumstances',
    'contribution.contact': 'Your contact info (optional)',
    'contribution.submit': 'Submit',
    
    // Moderation
    'moderation.title': 'Report content',
    'moderation.reason': 'Report reason',
    'moderation.reason.false_info': 'False information',
    'moderation.reason.duplicate': 'Duplicate',
    'moderation.reason.inappropriate': 'Inappropriate content',
    'moderation.reason.spam': 'Spam',
    'moderation.reason.other': 'Other',
    'moderation.details': 'Details (optional)',
    'moderation.contact': 'Your contact (optional)',
    'moderation.submit': 'Report',
    'moderation.success': 'Thank you for your report',
    
    // Timeline
    'timeline.sighting': 'Sighting reported',
    'timeline.info': 'Information received',
    'timeline.police_report': 'Reported to police',
    'timeline.found': 'Person found',
    'timeline.other': 'Other contribution',
    'timeline.created': 'Report created',
    
    // How to help
    'help.title': 'How to help?',
    'help.report.title': 'Report a disappearance',
    'help.report.desc': 'Fill out a complete form to report a missing person',
    'help.contribute.title': 'Provide information',
    'help.contribute.desc': 'Add information to an existing case if you have seen the person',
    'help.share.title': 'Share on social media',
    'help.share.desc': 'Spread the word to increase the chances of finding the missing',
    
    // Footer
    'footer.about': 'About',
    'footer.privacy': 'Privacy',
    'footer.terms': 'Terms of use',
    'footer.contact': 'Contact',
    'footer.countries': 'Countries covered',
    
    // PWA / Offline
    'offline.title': 'Offline mode',
    'offline.message': 'Some features are limited without connection',
    'offline.cached': 'Cached content available',
    
    // General
    'loading': 'Loading...',
    'error': 'An error occurred',
    'retry': 'Retry',
    'save': 'Save',
    'cancel': 'Cancel',
    'close': 'Close',
    'yes': 'Yes',
    'no': 'No',
    'or': 'or',
    'viewMore': 'View more',
    'noResults': 'No results',
    'success': 'Success',
  },
};

export const useI18n = create<I18nState>()(
  persist(
    (set, get) => ({
      language: 'fr',
      setLanguage: (lang: Language) => set({ language: lang }),
      t: (key: string) => {
        const lang = get().language;
        return translations[lang][key] || translations['fr'][key] || key;
      },
    }),
    {
      name: 'disparus-language',
    }
  )
);

// Helper to get browser language
export function getBrowserLanguage(): Language {
  const browserLang = navigator.language.split('-')[0];
  return browserLang === 'en' ? 'en' : 'fr';
}
