/**
 * Cookiebar functionality, as a TS/JS module.
 *
 * About modules: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules
 *
 * The code is organized here in a way to make the templates work with Django's page
 * cache. This means that anything user-specific (so different django session and even
 * cookie consent cookies) cannot be baked into the templates, as that breaks caches.
 *
 * The cookie bar operates on the following principles:
 *
 * - The developer using the library includes the desired template in their django
 *   templates, using the HTML <template> element. This contains the content for the
 *   cookie bar.
 * - The developer is responsible for loading some Javascript that loads this script.
 * - The main export of this script needs to be called (showCookieBar), with the
 *   appropriate options.
 * - The options include the backend URLs where the retrieve data, which selectors/DOM
 *   nodes to use for various functionality and the hooks to tap into the accept/decline
 *   life-cycle.
 * - When a user accepts or declines (all) cookies, the call to the backend is made via
 *   a fetch request, bypassing any page caches and preventing full-page reloads.
 */

/**
 * A serialized cookie group.
 *
 * See the backend model method `CookieGroup.as_json()`.
 */
export interface CookieGroup {
  varname: string;
  name: string;
  description: string;
  is_required: boolean;
}

export interface Options {
  statusUrl: string;
  // TODO: also accept element rather than selector?
  templateSelector: string;
  /**
   * DOM selector to the (script) tag holding the JSON-serialized cookie groups.
   *
   * This is typically rendered in a template with a template tag, e.g.
   *
   * ```django
   * {% all_cookie_groups 'cookie-consent__cookie-groups' %}
   * ```
   *
   * resulting in the selector: `'#cookie-consent__cookie-groups'`.
   */
  cookieGroupsSelector: string;
  acceptSelector: string;
  declineSelector: string;
  /**
   * Either a string (selector), DOMNode or null.
   *
   * If null, the bar is appended to the body. If provided, the node is used or looked
   * up.
   */
  insertBefore: string | HTMLElement | null;
  /**
   * Optional callback for when the cookie bar is being shown.
   *
   * You can use this to add a CSS class name to the body, for example.
   */
  onShow?: () => void;
  /**
   * Optional callback called when cookies are accepted.
   */
  onAccept?: (acceptedGroups: CookieGroup[], event?: MouseEvent) => void;
  /**
   * Optional callback called when cookies are accepted.
   */
  onDecline?: (declinedGroups: CookieGroup[], event?: MouseEvent) => void;
  /**
   * Name of the header to use for the CSRF token.
   *
   * If needed, this can be read/set via `settings.CSRF_HEADER_NAME` in the backend.
   */
  csrfHeaderName: string;
};

export interface CookieStatus {
  csrftoken: string;
  /**
   * Backend endpoint to POST to to accept the cookie groups.
   */
  acceptUrl: string;
  /**
   * Backend endpoint to POST to to decline the cookie groups.
   */
  declineUrl: string;
  /**
   * Array of accepted cookie group varnames.
   */
  acceptedCookieGroups: string[];
  /**
   * Array of declined cookie group varnames.
   */
  declinedCookieGroups: string[];
  /**
   * Array of undecided cookie group varnames.
   */
  notAcceptedOrDeclinedCookieGroups: string[];
}

const DEFAULT_FETCH_HEADERS: Record<string, string> = {
  'X-Cookie-Consent-Fetch': '1'
};

/**
 * A simple wrapper around window.fetch that understands the django-cookie-consent
 * backend endpoints.
 *
 * @private - while exported, use at your own risk. This class is not part of the
 * public API covered by SemVer.
 */
export class FetchClient {
  protected statusUrl: string;
  protected csrfHeaderName: string;
  protected cookieStatus: CookieStatus | null;

  constructor(statusUrl: string, csrfHeaderName: string) {
    this.statusUrl = statusUrl;
    this.csrfHeaderName = csrfHeaderName;
    this.cookieStatus = null;
  }

  async getCookieStatus(): Promise<CookieStatus> {
    if (this.cookieStatus === null) {
      const response = await window.fetch(
        this.statusUrl,
        {
          method: 'GET',
          credentials: 'same-origin',
          headers: DEFAULT_FETCH_HEADERS,
        }
      );
      this.cookieStatus = await response.json();
    }

    // type checker sanity check
    if (this.cookieStatus === null) {
      throw new Error('Unexpectedly received null cookie status');
    }
    return this.cookieStatus;
  };

  async saveCookiesStatusBackend (
    urlProperty: 'acceptUrl' | 'declineUrl',
    cookieGroups: CookieGroup[],
  ) {
    const cookieStatus = await this.getCookieStatus();
    const url = cookieStatus[urlProperty];
    if (!url) {
      throw new Error(`Missing url for ${urlProperty} - was the cookie status not loaded properly?`);
    }

    const formData = new FormData();
    for (const group of cookieGroups) {
      formData.append('cookie_groups', group.varname);
    }

    await window.fetch(url, {
      method: 'POST',
      body: formData,
      credentials: 'same-origin',
      headers: {
        ...DEFAULT_FETCH_HEADERS,
        [this.csrfHeaderName]: cookieStatus.csrftoken
      }
    });
  }
}

/**
 * Read the JSON script node contents and parse the content as JSON.
 *
 * The result is the list of available/configured cookie groups.
 * Use the status URL to get the accepted/declined status for an individual user.
 */
export const loadCookieGroups = (selector: string): CookieGroup[] => {
  const node = document.querySelector<HTMLScriptElement>(selector);
  if (!node) {
    throw new Error(`No cookie groups (script) tag found, using selector: '${selector}'`);
  }
  return JSON.parse(node.innerText);
};

const doInsertBefore = (beforeNode: HTMLElement, newNode: Node): void => {
  const parent = beforeNode.parentNode;
  if (parent === null) throw new Error('Reference node doesn\'t have a parent.');
  parent.insertBefore(newNode, beforeNode);
}

type RegisterEventsOptions = Pick<
  Options,
  'acceptSelector' | 'onAccept' | 'declineSelector' | 'onDecline'
> & Pick<
  CookieStatus,
  'acceptedCookieGroups' | 'declinedCookieGroups' | 'notAcceptedOrDeclinedCookieGroups'
> & {
  client: FetchClient,
  cookieBarNode: Element;
  cookieGroups: CookieGroup[];
}

/**
 * Register the accept/decline event handlers.
 *
 * Note that we can't just set the decline or accept cookie purely client-side, as the
 * cookie possibly has the httpOnly flag set.
 */
const registerEvents = ({
  client,
  cookieBarNode,
  cookieGroups,
  acceptSelector,
  onAccept,
  declineSelector,
  onDecline,
  acceptedCookieGroups: accepted,
  declinedCookieGroups: declined,
  notAcceptedOrDeclinedCookieGroups: undecided,
}: RegisterEventsOptions): void => {

  const acceptNode = cookieBarNode.querySelector<HTMLElement>(acceptSelector);
  if (acceptNode) {
    acceptNode.addEventListener('click', event => {
      event.preventDefault();
      const acceptedGroups = filterCookieGroups(cookieGroups, accepted.concat(undecided));
      onAccept?.(acceptedGroups, event);
      // trigger async action, but don't wait for completion
      client.saveCookiesStatusBackend('acceptUrl', acceptedGroups);
      cookieBarNode.parentNode!.removeChild(cookieBarNode);
    });
  }

  const declineNode = cookieBarNode.querySelector<HTMLElement>(declineSelector);
  if (declineNode) {
    declineNode.addEventListener('click', event => {
      event.preventDefault();
      const declinedGroups = filterCookieGroups(cookieGroups, declined.concat(undecided));
      onDecline?.(declinedGroups, event);
      // trigger async action, but don't wait for completion
      client.saveCookiesStatusBackend('declineUrl', declinedGroups);
      cookieBarNode.parentNode!.removeChild(cookieBarNode);
    });
  }
};

/**
 * Filter the cookie groups down to a subset of specified varnames.
 */
const filterCookieGroups = (cookieGroups: CookieGroup[], varNames: string[]) => {
  return cookieGroups.filter(group => varNames.includes(group.varname));
};

// See https://github.com/microsoft/TypeScript/issues/283
function cloneNode<T extends Node>(node: T) {
  return <T>node.cloneNode(true);
}

export const showCookieBar = async (options: Partial<Options> = {}): Promise<void> => {
  const {
    templateSelector = '#cookie-consent__cookie-bar',
    cookieGroupsSelector = '#cookie-consent__cookie-groups',
    acceptSelector = '.cookie-consent__accept',
    declineSelector = '.cookie-consent__decline',
    insertBefore = null,
    onShow,
    onAccept,
    onDecline,
    statusUrl = '',
    csrfHeaderName = 'X-CSRFToken', // Django's default, can be overridden with settings.CSRF_HEADER_NAME
  } = options;

  const cookieGroups = loadCookieGroups(cookieGroupsSelector);

  // no cookie groups -> abort, nothing to do
  if (!cookieGroups.length) return;

  const templateNode = document.querySelector<HTMLTemplateElement>(templateSelector);
  if (!templateNode) {
    throw new Error(`No (template) element found for selector '${templateSelector}'.`)
  }

  // insert before a given node, if specified, or append to the body as default behaviour
  const doInsert = insertBefore === null
    ? (cookieBarNode: Node) => document.querySelector('body')!.appendChild(cookieBarNode)
    : typeof insertBefore === 'string'
      ? (cookieBarNode: Node) => {
        const referenceNode = document.querySelector<HTMLElement>(insertBefore);
        if (referenceNode === null) throw new Error(`No element found for selector '${insertBefore}'.`)
        doInsertBefore(referenceNode, cookieBarNode);
      }
      : (cookieBarNode: Node) => doInsertBefore(insertBefore, cookieBarNode)
  ;

  if (!statusUrl) throw new Error('Missing status URL option, did you forget to pass the `statusUrl` option?');

  const client = new FetchClient(statusUrl, csrfHeaderName);
  const cookieStatus = await client.getCookieStatus();

  // calculate the cookie groups to invoke the callbacks. We deliberately fire those
  // without awaiting so that our cookie bar is shown/hidden as soon as possible.
  const {
    acceptedCookieGroups,
    declinedCookieGroups,
    notAcceptedOrDeclinedCookieGroups
  } = cookieStatus;

  const acceptedGroups = filterCookieGroups(cookieGroups, acceptedCookieGroups);
  if (acceptedGroups.length) onAccept?.(acceptedGroups);
  const declinedGroups = filterCookieGroups(cookieGroups, declinedCookieGroups);
  if (declinedGroups.length) onDecline?.(declinedGroups);

  // there are no (more) cookie groups to accept, don't show the bar
  if (!notAcceptedOrDeclinedCookieGroups.length) return;

  // grab the contents from the template node and add them to the DOM, optionally
  // calling the onShow callback
  const childToClone = templateNode.content.firstElementChild;
  if (childToClone === null) throw new Error('The cookie bar template element may not be empty.');
  const cookieBarNode = cloneNode(childToClone);
  registerEvents({
    client,
    cookieBarNode,
    cookieGroups,
    acceptSelector,
    onAccept,
    declineSelector,
    onDecline,
    acceptedCookieGroups,
    declinedCookieGroups,
    notAcceptedOrDeclinedCookieGroups,
  });
  doInsert(cookieBarNode);
  onShow?.();
};
